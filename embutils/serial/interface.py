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
from typing import Protocol, Optional

from ..utils import SDK_LOG, AbstractSerialized, EventHook, time_elapsed
from .device import Device
from .stream import Stream, AbstractSerializedStreamCodec


# -->> Definitions <<------------------
class ResponseCheckCallback(Protocol):
    """
    Response check callback signature:
    AbstractSerialized -> bool
    """
    def __call__(self, item: AbstractSerialized) -> bool: ...


# -->> API <<--------------------------
class Interface:
    """
    Serial command interface implementation.
    This class should implement all the methods to interact with the target device.

    Available events:

    #.  **on_received:** This event is emitted when an object is received and
        deserialized from the serial device. Subscribe using callbacks with
        syntax::

            def <callback>(item: AbstractSerialized)

    #.  **on_reconnect:** This event is emitted when the system is able to
        connect/reconnect to the device. Subscribe using callbacks with syntax::

            def <callback>()

    #.  **on_disconnect:** This event is emitted when the system gets
        disconnected from the device. Subscribe using callbacks with syntax::

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

    def __init__(self, codec: AbstractSerializedStreamCodec, port: str = None, looped: bool = False) -> None:
        """
        Class initialization.

        :param AbstractSerializedStreamCodec codec: Serialized objects codec handler.
        :param str port:                            Serial device port.
        :param bool looped:                         Enable test mode (looped serial).
        """
        # Response timeout configuration
        self._timeout = self.RESPONSE_TIMEOUT_S

        # Public events
        self.on_received = EventHook()
        self.on_reconnect = EventHook()
        self.on_disconnect = EventHook()

        # Stream: Communications thread
        # Start serial device
        if looped:
            serial = Device(looped=True, settings=self.SERIAL_SETTINGS)
        else:
            serial = Device(port=port, settings=self.SERIAL_SETTINGS)

        # Initialize stream and attach callbacks
        self._stream = Stream(device=serial, codec=codec)
        self._stream.on_reconnect  += self.on_reconnect.emit
        self._stream.on_disconnect += self.on_disconnect.emit
        self._stream.on_received   += self._process

        SDK_LOG.info(f'Interface initialized on: {self._stream.device}')

    @property
    def stream(self) -> Stream:
        """
        Stream handler.
        """
        return self._stream

    @property
    def timeout(self) -> float:
        """
        Message response timeout.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        """
        Message response timeout setter.

        :param float timeout: Timeout in seconds.
        """
        if timeout <= 0.0:
            raise ValueError('The response timeout needs to be greater than zero.')
        self._timeout = timeout

    def _process(self, item: AbstractSerialized) -> None:
        """
        Method used to handle the received items for processing.

        :param AbstractSerialized item: item to be processed.
        """
        # Do special actions:

        # Pass item to user:
        self.on_received.emit(item=item)

    def transmit(self,
                 send: AbstractSerialized,
                 logic: ResponseCheckCallback = None,
                 timeout: float = None) -> Optional[AbstractSerialized]:
        """
        Send a item and, if required, wait for a response that complies with
        the defined logic.

        The response detection logic should have the following syntax::

            def <callback>(AbstractSerialized)

        Where the input is the item received from the device.

        :param AbstractSerialized send:                     Item to be sent.
        :param Callable[[AbstractSerialized], bool] logic:  Response logic. Defines if a response is detected.
        :param float timeout:                               Response timeout. By default the interface setting.

        :returns: None if timeout or no response is detected, response item otherwise.
        :rtype: Optional[AbstractSerialized]
        """
        recv    = None
        timeout = self._timeout if (timeout is None) else timeout

        # Receive logic callback
        def on_received(item: AbstractSerialized) -> None:
            """
            Checks the received item against the response logic.
            """
            nonlocal send, recv
            if logic(item):
                recv = item

        # Prepare response logic
        if logic:
            self.on_received += on_received

        # Prepare and send
        SDK_LOG.debug('Sending item...')
        self._stream.send(item=send)

        # Define if response is needed
        if logic:
            # Wait for response
            SDK_LOG.debug('Waiting for response...')
            tm_start = time.time()
            while not recv and (time_elapsed(tm_start) < timeout):
                time.sleep(0.01)
            self.on_received -= on_received

            # Check data
            state = "Received" if recv else "Timeout"
            SDK_LOG.debug(f'Item response: {state} after {time_elapsed(start=tm_start):.03f}[s]')
            return recv

        # Return nothing if we don't need response
        SDK_LOG.debug('Response not needed.')
        return None

    def stop(self) -> None:
        """
        Stops the stream process.
        """
        self._stream.stop()

    def join(self) -> None:
        """
        Maintains the process alive while the interface is working. The loop will
        exit if the interface serial process gets stopped.
        """
        while self._stream.is_alive:
            time.sleep(0.5)
