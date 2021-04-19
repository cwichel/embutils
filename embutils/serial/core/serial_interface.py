#!/usr/bin/python
# -*- coding: ascii -*-
"""
Serial interface implementation.
This class represents the point closer to the user. Here the DEV has to
define/use payload/commands/frame layouts to communicate with the device.

NOTE: All the functions that interacts with the device (ex: read_serial_number)
should be defined here.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

import time
from embutils.serial.data import Frame, FrameHandler
from embutils.serial.core import FrameStream, SerialDevice
from embutils.utils.common import time_elapsed, EventHook, LOG_SDK, UsbID
from threading import Lock
from typing import Union


logger_sdk = LOG_SDK.logger


class SerialInterface:
    """Serial command interface implementation.
    This class implement all serial command wrappers and handlers.

    The available events are:
        1. on_port_reconnect: This event is emitted when the port is able to reconnect.
            Subscribe using callback with syntax:
                def <callback>()

        2. on_port_disconnect: This event is emitted when the port get disconnected.
            Subscribe using callback with syntax:
                def <callback>()

        3. on_frame_received: This event is emitted when a frame is received.
            Subscribe using callback with syntax:
                def <callback>(frame: Frame)
        """
    # Command wait response timeout
    RESPONSE_TIMEOUT_S = 0.5

    # Serial device settings
    SERIAL_SETTINGS = {
        'baudrate': 230400,
        'bytesize': 8,
        'stopbits': 1,
        'parity':   'N',
        'timeout':  0.1
        }

    def __init__(self, frame_handler: FrameHandler, port: str = None, looped: bool = False) -> None:
        """Class initialization.

        Args:
            frame_handler (FrameHandler): Handler used to process incoming frames.
            port (str): Serial device port.
            looped (bool): Enable test mode (looped serial).
        """
        # Add lock for multithreading usage
        self._lock = Lock()

        # Response timeout configuration
        self._timeout = self.RESPONSE_TIMEOUT_S

        # Public events
        self.on_port_reconnect = EventHook()
        self.on_port_disconnect = EventHook()
        self.on_frame_received = EventHook()

        # Frame Stream: Communications thread
        # Start serial device
        if looped:
            serial = SerialDevice(usb_id=UsbID(vid=0xDEAD, pid=0xBEEF), settings=self.SERIAL_SETTINGS, looped=True)
        else:
            serial = SerialDevice(port=port, settings=self.SERIAL_SETTINGS)

        # Initialize frame stream and attach callbacks
        self._frame_stream = FrameStream(serial_device=serial, frame_handler=frame_handler)
        self._frame_stream.on_port_reconnect  += self.on_port_reconnect.emit
        self._frame_stream.on_port_disconnect += self.on_port_disconnect.emit
        self._frame_stream.on_frame_received  += self._process_frame

        logger_sdk.info('Interface initialized on: {}'.format(self._frame_stream.serial_device))

    @property
    def lock(self) -> Lock:
        """Return the Command Interface lock for multithreading
        support.

        Return:
            Lock: Mutex.
        """
        return self._lock

    @property
    def frame_stream(self) -> FrameStream:
        """Return the current frame stream handler.

        Return:
            FrameStream: Handler used to send/receive frames over serial.
        """
        return self._frame_stream

    @property
    def timeout(self) -> float:
        """Returns the current response timeout.

        Return:
            float: Time in [s].
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: float) -> None:
        """Set the current response timeout.

        Args:
            value (float): Time in [s].
        """
        if value <= 0.0:
            raise ValueError('The response timeout needs to be greater than zero.')
        self._timeout = value

    def _process_frame(self, frame: Frame) -> None:
        """Method used to handle what to do when a frame is received.

        Args:
            frame (Frame): Frame to be processed.
        """
        # Do special actions:

        # Pass frame to user:
        self.on_frame_received.emit(frame=frame)

    def transmit(self, send: Frame, resp_logic: callable = None, resp_timeout: float = None) -> Union[None, Frame]:
        """Send a frame and wait for the response based on custom logic.
        The response detection callback syntax is:
            def <callback>(sent: Frame, recv: Frame)

        Args:
            send (Frame): Frame to be sent to the device.
            resp_logic (callable, optional): Response detection logic. The response detection is disabled when None.
            resp_timeout (float, optional): Response timeout. Use default interface timeout when None.

        Returns:
            Union[None, Frame]: None if timeout of no response detection is requested. If response detected Frame.
        """
        # SEND ------------------------
        # Prepare and send frame
        logger_sdk.debug('Sending frame...')
        self._frame_stream.send_frame(frame=send)

        # RECEIVE ---------------------
        # Return nothing if we don't need response
        if resp_logic is None:
            logger_sdk.debug('Response is not needed.')
            return None

        # Process wait response
        logger_sdk.debug('Waiting for frame response...')
        resp   = None
        ready  = False
        resp_timeout = self._timeout if (resp_timeout is None) else resp_timeout

        # Receive logic callback
        def on_frame_received(frame: Frame):
            nonlocal send, resp, resp_logic, ready
            ready = resp_logic(sent=send, recv=frame)
            if ready:
                resp = frame

        # Perform wait response logic
        self.on_frame_received += on_frame_received
        tm_start = time.time()
        while not ready and (time_elapsed(tm_start) < resp_timeout):
            time.sleep(0.01)
        self.on_frame_received -= on_frame_received

        # Check data
        logger_sdk.debug('Frame response: {state} after {elapsed:.03f}[s]'.format(
            state='Received' if ready else 'Timeout',
            elapsed=time_elapsed(start=tm_start)
            ))
        return resp

    def stop(self) -> None:
        """Stops the frame stream process.
        """
        self._frame_stream.stop()

    def join(self) -> None:
        """Maintains the process alive while the interface is working.
        """
        while self._frame_stream.is_alive:
            time.sleep(0.5)
