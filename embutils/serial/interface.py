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
import typing as tp

from ..utils import SDK_LOG, AbstractSerialized, EventHook, elapsed
from .stream import Stream


# -->> Definitions <<------------------
#: CallBack definition. AbstractSerialized -> bool
CBSerialized2Bool = tp.Callable[[AbstractSerialized], bool]


# -->> API <<--------------------------
class Interface:
    """
    Serial command interface implementation.
    This class should implement all the methods to interact with the target device.

    Available events:

    #.  **on_receive:** This event is emitted when an object is received and
        deserialized from the serial device. Subscribe using callbacks with
        syntax::

            def <callback>(item: AbstractSerialized)

    #.  **on_connect:** This event is emitted when the system is able to
        connect to the device. Subscribe using callbacks with syntax::

            def <callback>()

    #.  **on_reconnect:** This event is emitted when the system is able to
        reconnect to the device. Subscribe using callbacks with syntax::

            def <callback>()

    #.  **on_disconnect:** This event is emitted when the system gets
        disconnected from the device. Subscribe using callbacks with syntax::

            def <callback>()

    """
    #: Interface command pull period
    PERIOD_PULL_S = 0.005

    #: Interface join period
    PERIOD_JOIN_S = 0.5

    #: Interface command response timeout
    TIMEOUT_RESPONSE_S = 0.5

    def __init__(self, stream: Stream) -> None:
        """
        Class initialization.

        :param Stream stream:   Stream used to run the interface
        """
        # Response timeout configuration
        self._timeout = self.TIMEOUT_RESPONSE_S

        # Public events
        self.on_receive     = EventHook()
        self.on_connect     = EventHook()
        self.on_reconnect   = EventHook()
        self.on_disconnect  = EventHook()

        # Initialize stream and attach callbacks
        self._stream = stream
        self._stream.on_connect     += self.on_connect.emit
        self._stream.on_reconnect   += self.on_reconnect.emit
        self._stream.on_disconnect  += self.on_disconnect.emit
        self._stream.on_receive     += self._process

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

    def transmit(self,
                 send: AbstractSerialized,
                 logic: tp.Optional[CBSerialized2Bool] = None,
                 timeout: float = None) -> tp.Optional[AbstractSerialized]:
        """
        Send a item and, if required, wait for a response that complies with
        the defined logic.

        The response detection logic should have the following syntax::

            def <callback>(AbstractSerialized) -> bool:

        Where the input is the item received from the device.

        :param AbstractSerialized send:     Packet to be sent.
        :param CBSerialized2Bool logic:     Response logic. Defines if a response is detected. If none then only sends.
        :param float timeout:               Response timeout. By default the interface setting.

        :returns: None if timeout or no response is detected, response item otherwise.
        :rtype: Optional[AbstractSerialized]
        """
        if logic:
            return self._send_recv(send=send, logic=logic, timeout=timeout)
        self._send_none(send=send)
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
            time.sleep(self.PERIOD_JOIN_S)

    def _process(self, item: AbstractSerialized) -> None:
        """
        Method used to handle the received items for processing.

        :param AbstractSerialized item: item to be processed.
        """
        # Do special actions:

        # Pass item to user:
        self.on_receive.emit(item=item)

    def _send_none(self,
                   send: AbstractSerialized) -> None:
        """
        Sends an item and dont care about the response.

        :param AbstractSerialized send:     Packet to be sent.
        """
        # Send item and return
        SDK_LOG.debug('Sending item...')
        self._stream.send(item=send)
        SDK_LOG.debug('Response not needed.')

    def _send_recv(self,
                   send: AbstractSerialized,
                   logic: CBSerialized2Bool,
                   timeout: float = None) -> tp.Optional[AbstractSerialized]:
        """
        Sends an item and wait for response.

        :param AbstractSerialized send:     Item to be sent.
        :param CBSerialized2Bool logic:     Response logic. Defines if a response is detected. If none then only sends.
        :param float timeout:               Response timeout. By default the interface setting.

        :returns: None if timeout or no response is detected, response item otherwise.
        :rtype: Optional[AbstractSerialized]
        """
        # Prepare data
        recv = None
        timeout = self._timeout if (timeout is None) else timeout

        # Receive logic callback
        def on_received(item: AbstractSerialized) -> None:
            nonlocal recv
            if logic(item):
                recv = item

        # Prepare response logic
        self.on_receive += on_received

        # Prepare and send
        SDK_LOG.debug('Sending item...')
        self._stream.send(item=send)

        # Wait for response
        SDK_LOG.debug('Waiting for response...')
        tm_start = time.time()
        while not recv and (elapsed(tm_start) < timeout):
            time.sleep(self.PERIOD_PULL_S)
        self.on_receive -= on_received

        # Check data
        state = "Received" if recv else "Timeout"
        SDK_LOG.debug(f'Item response: {state} after {elapsed(start=tm_start):.03f}[s]')
        return recv
