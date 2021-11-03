#!/usr/bin/python
# -*- coding: ascii -*-
"""
Stream implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import abc
import time
import typing as tp

from ..utils.events import EventHook
from ..utils.serialized import AbstractSerialized, AbstractSerializedCodec
from ..utils.service import AbstractService
from ..utils.threading import SimpleThreadTask
from .device import Device


# -->> Definitions <<------------------


# -->> API <<--------------------------
class AbstractSerializedStreamCodec(AbstractSerializedCodec):
    """
    AbstractSerializedCodec variant for stream usage.
    This class includes the logic required to decode a serialized object from a byte stream.
    """
    @abc.abstractmethod
    def decode_stream(self, device: Device) -> tp.Optional[AbstractSerialized]:
        """
        Decodes a serialized object from a byte stream.

        :param Device device: Stream source.

        :returns: Deserialized object if able, None otherwise.
        :rtype: Optional[AbstractSerialized]

        :raises ConnectionError: Device raised exception while reading.
        """


class Stream(AbstractService):
    """
    This class is used to send and receive serialized objects through a serial device
    in asynchronous way. When a new item is received this class will notify the system
    using events.

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
    #: Stream reconnect period
    RECONNECT_PERIOD_S = 0.5

    def __init__(self, *args, device: Device, codec: AbstractSerializedStreamCodec, **kwargs) -> None:
        """
        Class initialization.

        :param Device device:                       Serial device handler.
        :param AbstractSerializedStreamCodec codec: Serialized objects codec handler.
        """
        # Service core
        super().__init__(*args, **kwargs)
        self._device        = device
        self._codec         = codec
        # Service events
        self.on_receive     = EventHook()
        self.on_connect     = EventHook()
        self.on_reconnect   = EventHook()
        self.on_disconnect  = EventHook()
        # Handle public events
        self.on_receive     += lambda item: self._transfer_debug(item=item, received=True)

    def __del__(self) -> None:
        """
        Class destructor.
        Stops the stream and the associated serial device.
        """
        super().__del__()
        del self._device

    @property
    def codec(self) -> AbstractSerializedStreamCodec:
        """
        Serialized objects codec handler.
        """
        return self._codec

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

    def send(self, item: AbstractSerialized) -> None:
        """
        Send a serializable item through the serial device.

        :param AbstractSerialized item: Item to send.
        """
        if self.is_running:
            self._transfer_debug(item=item, received=False)
            self._device.write(data=self._codec.encode(data=item))

    def _task(self) -> None:
        """
        Stream process:

        #. Tries to decode items.
        #. If an item is available, emits an event.
        #. Handle disconnection status.

        """
        # Try to receive data, if failed go to reconnection loop
        try:
            item = self._codec.decode_stream(device=self._device)
            if item:
                self._pool.enqueue(task=SimpleThreadTask(
                    name=f"{self.__class__.__name__}.on_received",
                    task=lambda: self.on_receive.emit(item=item)
                    ))

        except ConnectionError:
            # Device disconnected...
            self._logger.info(f"Device disconnected: {self._device}")
            self._pool.enqueue(task=SimpleThreadTask(
                name=f"{self.__class__.__name__}.on_disconnect",
                task=self.on_disconnect.emit
                ))
            if self._device_connect():
                self._pool.enqueue(task=SimpleThreadTask(
                    name=f"{self.__class__.__name__}.on_reconnect",
                    task=self.on_reconnect.emit
                    ))

    def _on_start(self) -> None:
        """
        Ensures device connected on service start.
        """
        self._device_init()

    def _on_resume(self) -> None:
        """
        Ensures device connected on service resume.
        """
        self._device_init(start=False)

    def _on_pause(self) -> None:
        """
        Closes device when paused.
        """
        self._device.close()

    def _on_end(self) -> None:
        """
        Closes device when service gets terminated.
        """
        self._device.close()

    def _device_init(self, start: bool = True) -> None:
        """
        Initializes the serial device.

        :param bool start:  True if used on start handler. False otherwise.
        """
        if not self._device.is_open:
            connected = self._device_connect()
            if connected and start:
                self._pool.enqueue(task=SimpleThreadTask(
                    name=f"{self.__class__.__name__}.on_connect",
                    task=self.on_connect.emit
                    ))

    def _device_connect(self) -> bool:
        """
        Perform connection attempts on the serial device while the service is running.

        :returns: True if connection succeeded, false otherwise.
        :rtype: bool
        """
        self._logger.info(f"Attempting connection to {self._device}")
        self._device.close()
        while self.is_running:
            if self._device.open():
                self._device.flush()
                self._logger.info(f"Connected to {self._device}")
                return True
            self._logger.info(f"Connection attempt on {self._device} failed.")
            time.sleep(self.RECONNECT_PERIOD_S)
        return False

    def _transfer_debug(self, item: AbstractSerialized, received: bool) -> None:
        """
        Print the sent/received items on the logger:

        :param AbstractSerialized item: Item that is being sent/received.
        :param bool received:           Flag to indicate if we are sending/receiving the item.
        """
        action = "recv" if received else "sent"
        self._logger.debug(f"Item {action}: {item}")
