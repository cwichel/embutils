#!/usr/bin/python
# -*- coding: ascii -*-
"""
Frame stream implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import time
from embutils.serial.data import Frame, FrameHandler
from embutils.serial.core.serial_device import SerialDevice
from embutils.utils import EventHook, LOG_SDK, ThreadItem


logger_sdk = LOG_SDK.logger


class FrameStream:
    """
    This class is used to send and receive frames through the serial device in an
    asynchronous way. When a new frame is received this class will notify the system
    using events.

    Available events:

    #.  **on_frame_received:** This event is emitted when a frame is received
        and deserialized from the serial device. Subscribe using callbacks with
        syntax::

            def <callback>(frame: Frame)

    #.  **on_port_reconnect:** This event is emitted when the system is able to
        reconnect to the configured port. Subscribe using callbacks with syntax::

            def <callback>()

    #.  **on_port_disconnect:** This event is emitted when the system gets
        disconnected from the configured serial port. Subscribe using callbacks
        with syntax::

            def <callback>()

    """
    def __init__(self, serial_device: SerialDevice, frame_handler: FrameHandler) -> None:
        """
        Class initialization.

        :param SerialDevice serial_device: Serial device interface. Used to read/write
            from the serial.
        :param FrameHandler frame_handler: Frame handler. Used to read and decode the
            incoming bytes into a frame.
        """
        # Initialize
        self._serial_device = serial_device
        self._frame_handler = frame_handler

        # Events
        self.on_frame_received = EventHook()
        self.on_port_reconnect = EventHook()
        self.on_port_disconnect = EventHook()

        # Debug prints for received
        self.on_frame_received += lambda frame: self._print_debug(frame=frame, received=True)

        # Thread related
        self._is_active = True
        self._is_paused = False
        self._pause_active = False
        self._thread = ThreadItem(name=self.__class__.__name__, target=self._process)

    def __del__(self) -> None:
        """
        Class destructor. Stops the stream thread and removes the associated
        serial device.
        """
        if self._is_active:
            self.stop()
        del self._serial_device

    @property
    def serial_device(self) -> SerialDevice:
        """
        Get the serial device handler.

        :returns: Serial device handler.
        :rtype: SerialDevice
        """
        return self._serial_device

    @serial_device.setter
    def serial_device(self, handler: SerialDevice) -> None:
        """
        Set the serial device handler.

        .. note::
            *   This action replaces the current serial device.
            *   If the new serial device handler has no port defined
                the current port is preserved.

        :param SerialDevice handler: Serial device handler.
        """
        self.pause()
        if handler.port is not None:
            self._serial_device = handler
        self.resume()

    @property
    def frame_handler(self) -> FrameHandler:
        """
        Get the frame handler.

        :returns: Frame handler.
        :rtype: FrameHandler
        """
        return self._frame_handler

    @frame_handler.setter
    def frame_handler(self, handler: FrameHandler) -> None:
        """
        Set the frame handler.

        :param FrameHandler handler: Frame handler.
        """
        self.pause()
        if handler:
            self._frame_handler = handler
        self.resume()

    @property
    def is_alive(self) -> bool:
        """
        Returns if the stream thread is alive.

        :returns: True if alive, false otherwise.
        :rtype: bool
        """
        return self._thread.is_alive()

    @property
    def is_working(self) -> bool:
        """
        Returns if the stream thread is working (not paused).

        :returns: True if working, false otherwise.
        :rtype: bool
        """
        return self.is_alive and self._serial_device.is_open and not self._is_paused

    def send_frame(self, frame: Frame) -> None:
        """
        Send a frame through the serial device.

        :param Frame frame: Frame to send.
        """
        if self.is_working:
            self._print_debug(frame=frame, received=False)
            self._serial_device.write(data=frame.serialize())

    def resume(self) -> None:
        """
        Resume the stream data transmission.
        """
        if self.is_alive and self._serial_device.open():
            self._serial_device.flush()
            self._is_paused = False
            self._pause_active = False
            logger_sdk.info('Stream resumed.')

    def pause(self) -> None:
        """
        Pauses the stream data transmission.
        """
        if self.is_working:
            self._is_paused = True
            while not self._pause_active:
                time.sleep(0.01)
            self._serial_device.close()
            logger_sdk.info('Stream paused.')

    def stop(self) -> None:
        """
        Stops the stream transmission and kills the thread.
        """
        self._is_active = False
        while self._thread.is_alive():
            time.sleep(0.01)
        self._serial_device.close()
        logger_sdk.info('Stream stopped.')

    def _process(self) -> None:
        """
        Frame stream process:

        #. Read bytes depending on the requirements of the frame handler.
        #. Process bytes, parses frames and raises events.
        #. Handle disconnection status.

        """
        logger_sdk.info('Frame stream started.')

        # Do this periodically
        while self._is_active:
            # Pause state
            if self._is_paused:
                if not self._pause_active:
                    self._pause_active = True
                time.sleep(0.01)
                continue

            # Receive and process data
            if not self._frame_handler.read_process(serial=self._serial_device, emitter=self.on_frame_received):
                # Device disconnected...
                logger_sdk.info(f'Device disconnected: {self._serial_device}')
                ThreadItem(
                    name=f'{self.__class__.__name__}.on_port_disconnect',
                    target=self.on_port_disconnect.emit
                    )
                if self._reconnect():
                    ThreadItem(
                        name=f'{self.__class__.__name__}.on_port_reconnect',
                        target=self.on_port_reconnect.emit
                        )

            # Give some time
            time.sleep(0.01)

    def _reconnect(self) -> bool:
        """
        Performs a reconnection attempt with the serial device.

        :returns: True if reconnection succeeded, false otherwise.
        :rtype: bool
        """
        status = False
        self._serial_device.close()
        logger_sdk.info(f'Starting reconnection attempt on {self._serial_device}')
        while self._is_active:
            if self._serial_device.open():
                logger_sdk.info(f'Device {self._serial_device} reconnected.')
                status = True
                break
            else:
                logger_sdk.info(f'Reconnection attempt on {self._serial_device} failed.')
                time.sleep(0.5)
        return status

    @staticmethod
    def _print_debug(frame: Frame, received: bool) -> None:
        """
        Prints the received/sent frames on the SDK logger:

        :param Frame frame: Frame that is being sent/received.
        :param bool received: Flag to indicate if we are sending/receiving the frame.
        """
        action = 'recv' if received else 'sent'
        logger_sdk.debug(f'Frame {action}: {frame}')
