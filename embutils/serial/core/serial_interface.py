#!/usr/bin/python
# -*- coding: ascii -*-
"""
Serial interface implementation. This class represents the closer point to the
user. Here the developer needs to complete the interface with the specific
applications commands.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import time
from embutils.serial.data import Frame, FrameHandler
from embutils.serial.core import FrameStream, SerialDevice
from embutils.utils import time_elapsed, EventHook, LOG_SDK, UsbID
from typing import Union


logger_sdk = LOG_SDK.logger


class SerialInterface:
    """
    Serial command interface implementation. This class should implement all the
    methods to interact with the target device.

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
    #: Interface command response timeout
    RESPONSE_TIMEOUT_S = 0.5

    #: Default serial device settings
    SERIAL_SETTINGS = {
        'baudrate': 230400,
        'bytesize': 8,
        'stopbits': 1,
        'parity':   'N',
        'timeout':  0.1
        }

    def __init__(self, frame_handler: FrameHandler, port: str = None, looped: bool = False) -> None:
        """
        Class initialization.

        :param FrameHandler frame_handler: Frame handler. Used to read and decode the
            incoming bytes into a frame.
        :param str port:    Serial device port.
        :param bool looped: Enable test mode (with looped serial).
        """
        # Response timeout configuration
        self._timeout = self.RESPONSE_TIMEOUT_S

        # Public events
        self.on_frame_received = EventHook()
        self.on_port_reconnect = EventHook()
        self.on_port_disconnect = EventHook()

        # Frame Stream: Communications thread
        # Start serial device
        if looped:
            serial = SerialDevice(uid=UsbID(vid=0xDEAD, pid=0xBEEF), settings=self.SERIAL_SETTINGS, looped=True)
        else:
            serial = SerialDevice(port=port, settings=self.SERIAL_SETTINGS)

        # Initialize frame stream and attach callbacks
        self._frame_stream = FrameStream(serial_device=serial, frame_handler=frame_handler)
        self._frame_stream.on_port_reconnect  += self.on_port_reconnect.emit
        self._frame_stream.on_port_disconnect += self.on_port_disconnect.emit
        self._frame_stream.on_frame_received  += self._process_frame

        logger_sdk.info(f'Interface initialized on: {self._frame_stream.serial_device}')

    @property
    def frame_stream(self) -> FrameStream:
        """
        Frame stream handler.
        """
        return self._frame_stream

    @property
    def timeout(self) -> float:
        """
        Message response timeout.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        """
        Set the interface message response timeout.

        :param float timeout: Timeout in seconds.
        """
        if timeout <= 0.0:
            raise ValueError('The response timeout needs to be greater than zero.')
        self._timeout = timeout

    def _process_frame(self, frame: Frame) -> None:
        """
        Method used to handle the received frames for processing.

        :param Frame frame: Frame to be processed.
        """
        # Do special actions:

        # Pass frame to user:
        self.on_frame_received.emit(frame=frame)

    def transmit(self, send: Frame, logic: callable = None, timeout: float = None) -> Union[None, Frame]:
        """
        Send a frame and, if required, wait for a response that complies with
        the defined response logic.

        The response detection logic callback should have the following syntax::

            def <callback>(sent: Frame, recv: Frame)

        Where:

        * `sent`: Frame sent (if required for comparisons.
        * `recv`: Frame received from the target.

        :param Frame send:      Frame to send to target.
        :param callable logic:  Response logic. Defines how the response is detected.
        :param float timeout:   Response timeout. If none it'll use the default interface timeout.

        :returns: None if timeout or no response is detected, response frame otherwise.
        :rtype: Frame
        """
        recv    = None
        timeout = self._timeout if (timeout is None) else timeout

        # Receive logic callback
        def on_frame_received(frame: Frame):
            """Performs the response logic and returns a frame if succeed.
            """
            nonlocal send, recv
            if logic(sent=send, recv=frame):
                recv = frame

        # Prepare response logic
        if logic:
            self.on_frame_received += on_frame_received

        # Prepare and send frame
        logger_sdk.debug('Sending frame...')
        self._frame_stream.send_frame(frame=send)

        # Define if response is needed
        if logic:
            # Wait for response
            logger_sdk.debug('Waiting for response...')
            tm_start = time.time()
            while not recv and (time_elapsed(tm_start) < timeout):
                time.sleep(0.01)
            self.on_frame_received -= on_frame_received

            # Check data
            state = "Received" if recv else "Timeout"
            logger_sdk.debug(f'Frame response: {state} after {time_elapsed(start=tm_start):.03f}[s]')
            return recv

        else:
            # Return nothing if we don't need response
            logger_sdk.debug('Response not needed.')
            return None

    def stop(self) -> None:
        """
        Stops the frame stream process.
        """
        self._frame_stream.stop()

    def join(self) -> None:
        """
        Maintains the process alive while the interface is working. The loop will
        exit if the interface serial process gets stopped.
        """
        while self._frame_stream.is_alive:
            time.sleep(0.5)
