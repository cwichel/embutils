#!/usr/bin/python
# -*- coding: ascii -*-
"""
Stream implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import time

from abc import abstractmethod
from typing import Optional

from ..utils import SDK_LOG, SDK_TP, AbstractSerialized, AbstractSerializedCodec, EventHook, SimpleThreadTask
from .device import Device


# -->> Definitions <<------------------


# -->> API <<--------------------------
class AbstractSerializedStreamCodec(AbstractSerializedCodec):
    """
    AbstractSerializedCodec variant for stream usage.
    This class includes the logic required to decode a serialized object from a byte stream.
    """
    @abstractmethod
    def decode_stream(self, device: Device) -> Optional[AbstractSerialized]:
        """
        Decodes a serialized object from a byte stream.

        :param Device device: Stream source.

        :returns: Deserialized object if able, None otherwise.
        :rtype: Optional[AbstractSerialized]

        :raises ConnectionError: Device raised exception while reading.
        """
        pass


class Stream:
    """
    This class is used to send and receive serialized objects through a serial device
    in asynchronous way. When a new item is received this class will notify the system
    using events.

    Available events:

    #.  **on_received:** This event is emitted when an object is received and
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
    #: Stream pull period
    PERIOD_PULL_S = 0.005

    #: Stream reconnect try period
    PERIOD_RECONNECT_S = 0.5

    def __init__(self, device: Device, codec: AbstractSerializedStreamCodec) -> None:
        """
        Class initialization.

        :param Device device:                       Serial device handler.
        :param AbstractSerializedStreamCodec codec: Serialized objects codec handler.
        """
        # Initialize
        self._device = device
        self._codec  = codec

        # Events
        self.on_received    = EventHook()
        self.on_connect     = EventHook()
        self.on_reconnect   = EventHook()
        self.on_disconnect  = EventHook()

        # Debug prints for received
        self.on_received += lambda item: self._print_debug(item=item, received=True)

        # Start thread
        self._active    = True
        self._finished  = False
        self._paused    = False     # enables pause?
        self._in_pause  = False     # tells if we are actually on pause state
        SDK_TP.enqueue(task=SimpleThreadTask(
            name=f"{self.__class__.__name__}.process",
            task=self._process
            ))

    def __del__(self) -> None:
        """
        Class destructor.
        Stops the stream and the associated serial device.
        """
        if self.is_alive:
            self.stop()
        del self._device

    @property
    def device(self) -> Device:
        """
        Serial device handler.
        """
        return self._device

    @device.setter
    def device(self, device: Device) -> None:
        """
        Serial device handler setter.

        .. note::
            *   This action replaces the current device.
            *   If the new device handler has no port defined
                the current port is preserved.

        :param Device device: Serial device handler.
        """
        self.pause()
        if device.port is not None:
            self._device = device
        self.resume()

    @property
    def codec(self) -> AbstractSerializedStreamCodec:
        """
        Serialized objects codec handler.
        """
        return self._codec

    @property
    def is_alive(self) -> bool:
        """
        Returns if the stream thread is alive.
        """
        return self._active or not self._finished

    @property
    def is_working(self) -> bool:
        """
        Returns if the stream thread is working (not paused).
        """
        return self.is_alive and self._device.is_open and not self._paused

    def send(self, item: AbstractSerialized) -> None:
        """
        Send a serializable item through the serial device.

        :param AbstractSerialized item: Item to send.
        """
        if self.is_working:
            self._print_debug(item=item, received=False)
            self._device.write(data=self._codec.encode(data=item))

    def resume(self) -> None:
        """
        Resume the stream transmission.
        """
        if self.is_alive and self._device.open():
            self._device.flush()
            self._paused = False
            self._in_pause = False
            SDK_LOG.info('Stream resumed.')

    def pause(self) -> None:
        """
        Pauses the stream transmission.
        """
        if self.is_working:
            self._paused = True
            while not self._in_pause:
                time.sleep(0.01)
            self._device.close()
            SDK_LOG.info('Stream paused.')

    def stop(self) -> None:
        """
        Stops the stream transmission and kills the thread.
        """
        self._active = False
        while self.is_alive:
            time.sleep(0.01)
        self._device.close()
        SDK_LOG.info('Stream stopped.')

    def _process(self) -> None:
        """
        Stream process:

        #. Tries to decode items.
        #. If an item is available, emits an event.
        #. Handle disconnection status.

        """
        SDK_LOG.info('Stream started.')

        # Connect to device if not connected
        if not self._device.is_open and self._reconnect():
            SDK_TP.enqueue(task=SimpleThreadTask(
                name=f"{self.__class__.__name__}.on_connect",
                task=self.on_connect.emit
                ))

        # Do this periodically
        while self._active:
            # Handle pause
            if self._paused:
                self._process_paused()
                continue
            # Handle reading
            self._process_active()

        # Inform finished
        self._finished = True

    def _process_paused(self):
        """
        Handle process pause state.
        """
        # Inform that pause started
        if not self._in_pause:
            self._in_pause = True

        # Delay...
        time.sleep(0.01)

    def _process_active(self):
        """
        Handle process active state.
        """
        # Try to receive data, if failed go to reconnection loop
        try:
            item = self._codec.decode_stream(device=self._device)
            if item:
                SDK_TP.enqueue(task=SimpleThreadTask(
                    name=f"{self.__class__.__name__}.on_received",
                    task=lambda recv=item: self.on_received.emit(item=recv)
                    ))

        except ConnectionError:
            # Device disconnected...
            SDK_LOG.info(f'Device disconnected: {self._device}')
            SDK_TP.enqueue(task=SimpleThreadTask(
                name=f"{self.__class__.__name__}.on_disconnect",
                task=self.on_disconnect.emit
                ))
            if self._reconnect():
                SDK_TP.enqueue(task=SimpleThreadTask(
                    name=f"{self.__class__.__name__}.on_reconnect",
                    task=self.on_reconnect.emit
                    ))

        # Delay...
        time.sleep(self.PERIOD_PULL_S)

    def _reconnect(self) -> bool:
        """
        Performs a reconnection attempt with the serial device.

        :returns: True if reconnection succeeded, false otherwise.
        :rtype: bool
        """
        status = False
        self._device.close()
        SDK_LOG.info(f'Starting connection attempt on {self._device}')
        while self._active:
            if self._device.open():
                SDK_LOG.info(f'Device {self._device} connected.')
                status = True
                break
            SDK_LOG.info(f'Connection attempt on {self._device} failed.')
            time.sleep(self.PERIOD_RECONNECT_S)
        return status

    @staticmethod
    def _print_debug(item: AbstractSerialized, received: bool) -> None:
        """
        Prints the received/sent items on the SDK logger:

        :param AbstractSerialized item: Item that is being sent/received.
        :param bool received:           Flag to indicate if we are sending/receiving the item.
        """
        action = 'recv' if received else 'sent'
        SDK_LOG.debug(f'Item {action}: {item}')
