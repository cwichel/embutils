#!/usr/bin/env python
##
# @file       frame_stream.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Implements a serial process to send/receive frames.
# =============================================================================

import time
from embutils.utils.common import EventHook, LOG_SDK, ThreadItem
from embutils.serial_process.data import Frame, FrameHandler
from embutils.serial_process.core.serial_device import SerialDevice


logger_sdk = LOG_SDK.logger


class FrameStream:
    """Frame stream implementation.
    This class is used to send and receive frames through the serial device
    in an asynchronous way. When a new frame is received this class will notify
    using events.

    The available events are:
        1. on_frame_receive: This event is emitted when a frame is received.
            Subscribe using callback with syntax:
                def <callback>(frame: Frame)

        2. on_port_reconnect: This event is emitted when the port is able to reconnect.
            Subscribe using callback with syntax:
                def <callback>()

        3. on_port_disconnect: This event is emitted when the port get disconnected.
            Subscribe using callback with syntax:
                def <callback>()
    """
    def __init__(self, serial_device: SerialDevice, frame_handler: FrameHandler) -> None:
        """Class constructor. Initialize the frame stream.

        Args:
            serial_device (SerialDevice): Used to read/write from serial.
            frame_handler (FrameHandler): Used to interpret the incoming bytes as a frame.
        """
        # Initialize
        self._serial_device = serial_device
        self._frame_handler = frame_handler

        # Events
        self.on_frame_received = EventHook()
        self.on_port_reconnect = EventHook()
        self.on_port_disconnect = EventHook()

        # Thread related
        self._is_active = True
        self._is_paused = False
        self._pause_active = False
        self._thread = ThreadItem(name=self.__class__.__name__, target=self._process)

    def __del__(self) -> None:
        """Class destructor. Stop the thread and remove the associated serial device.
        """
        self.stop()
        del self._serial_device

    @property
    def is_alive(self) -> bool:
        """Return if the thread is alive.

        Returns:
            bool: True if alive, false otherwise.
        """
        return self._thread.is_alive()

    @property
    def is_working(self) -> bool:
        """Return if the process is being executed.

        Returns;
            bool: True if working, false if stopped or paused.
        """
        return self.is_alive and self._serial_device.is_open and not self._is_paused

    def send_frame(self, frame: Frame) -> None:
        """Send the specified frame using the serial device.

        Args:
            frame (Frame): Frame to be sent.
        """
        if self.is_working:
            raw = frame.raw
            ser = frame.serialize()
            self._serial_device.write(data=ser)
            logger_sdk.debug("Frame sent:\r\n > Raw : {}\r\n > Ser : {}".format(raw, ser))

    def resume(self) -> None:
        """Resume the data transmission.
        """
        if self.is_alive and self._serial_device.open():
            self._serial_device.flush()
            self._is_paused = False
            self._pause_active = False
            logger_sdk.info("Stream resumed.")

    def pause(self) -> None:
        """Pause the data transmission.
        """
        if self.is_working:
            self._is_paused = True
            while not self._pause_active:
                time.sleep(0.01)
            self._serial_device.close()
            logger_sdk.info("Stream paused.")

    def stop(self) -> None:
        """Stop the transmission and kill the thread.
        """
        self._is_active = True
        while self._thread.is_alive():
            time.sleep(0.01)
        logger_sdk.info("Stream stopped.")

    def _process(self) -> None:
        """Frame transmission main loop.
        This loop handle the frame reception:
            1. Read the FrameHandler required bytes.
            2. Send the bytes to be processed by the FrameHandler.
            3. Handle disconnection status.
        """
        logger_sdk.info("Scanner started.")

        # Do this periodically
        while self._is_active:
            # Pause state
            if self._is_paused:
                if not self._pause_active:
                    self._pause_active = True
                time.sleep(0.01)
                continue

            # Receive and process data
            bytes_recv = self._serial_device.read(size=self._frame_handler.bytes_to_read)
            if bytes_recv is not None:
                # Bytes received without issues
                self._frame_handler.process(new_bytes=bytes_recv, emitter=self.on_frame_received)
            else:
                # Device disconnected...
                logger_sdk.info("Device disconnected: {}".format(self._serial_device))
                ThreadItem(
                    name='{}.{}'.format(self.__class__.__name__, 'on_port_disconnect'),
                    target=self.on_port_disconnect
                    )
                if self._reconnect():
                    ThreadItem(
                        name='{}.{}'.format(self.__class__.__name__, 'on_port_reconnect'),
                        target=self.on_port_reconnect
                        )

    def _reconnect(self) -> bool:
        """Start a reconnection attempt to the serial device.

        Returns:
            bool: True if reconnection succeeded, false otherwise.
        """
        status = False
        self._serial_device.close()
        logger_sdk.info("Starting reconnection attempt on {}".format(self._serial_device))
        while self._is_active:
            if self._serial_device.open():
                logger_sdk.info("Device {} reconnected.".format(self._serial_device))
                status = True
                break
            else:
                logger_sdk.info("Reconnection attempt on {} failed.".format(self._serial_device))
                time.sleep(0.5)
        return status
