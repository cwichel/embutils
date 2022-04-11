#!/usr/bin/python
# -*- coding: ascii -*-
"""
This example shows how to define the required components to use
the serial stream.

We need to:

- Define a packet (serializable message structure).
- Define a framing codec (how the packet is sent trough serial).

In this example:

- The packet defines: source, destination, payload and checksum.
- COBS is used for framing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from typing import Optional, Type

import attr

from embutils.utils import AbstractSerialized, COBS, CRC
from embutils.serial import AbstractSerializedStreamCodec, Device


# -->> Definitions <<------------------


# -->> API <<--------------------------
@attr.define
class SimplePacket(AbstractSerialized):
    """
    Simple packet implementation.

    #. Source ID:        uint8_t
    #. Destination ID:   uint8_t
    #. Length:           uint8_t
    #. Payload:          length * uint_8
    #. CRC16:            uint16_t
    """
    #: CRC model
    CRC16 = CRC()
    #: Message source
    source:         int = attr.field(converter=int)
    #: Message destination
    destination:    int = attr.field(converter=int)
    #: Message payload
    payload:        bytearray = attr.field(converter=bytearray)

    @property
    def crc(self) -> int:
        """
        CRC value.
        """
        return self.CRC16.compute(data=self._core())

    @property
    def length(self) -> int:
        """
        Payload length.
        """
        return len(self.payload)

    def _core(self) -> bytearray:
        """
        Contents without the CRC bytes.
        """
        return bytearray([self.source, self.destination, len(self.payload)]) + self.payload

    def serialize(self) -> bytearray:
        """
        Convert the packet object into bytes.
        """
        return bytearray(
            self._core() +
            self.crc.to_bytes(length=2, byteorder="little", signed=False)
            )

    @classmethod
    def deserialize(cls, data: bytearray) -> Optional["SimplePacket"]:
        """
        Deserialize the packet from the input bytes.
        """
        # Check sufficient data
        if len(data) < 5:
            return None

        # Deserialize the data into a frame
        data_len = data[2]
        frame_crc = int.from_bytes(bytes=data[-2:], byteorder="little", signed=False)
        frame = SimplePacket(
            source=data[0],
            destination=data[1],
            payload=data[3:-2],
            )

        # Verify contents
        if (frame.crc == frame_crc) and (frame.length == data_len):
            return frame
        return None


class COBSStreamFramingCodec(AbstractSerializedStreamCodec):
    """
    COBS framing implementation for use on streams.
    """
    def __init__(self, dtype: Type[AbstractSerialized]):
        """
        Initializes the codec with the expected serialized type.
        """
        self._dtype = dtype

    def encode(self, data: AbstractSerialized) -> bytearray:
        """
        Encode the input bytes using COBS.
        """
        ser = data.serialize()
        enc = COBS.encode(data=ser)
        return enc

    def decode(self, data: bytearray) -> Optional[AbstractSerialized]:
        """
        Decodes the input bytes using COBS and tries to deserialize the packet.
        """
        try:
            dec = COBS.decode(data=data)
            obj = self._dtype.deserialize(data=dec)
            return obj
        except Exception as _:
            return None

    def decode_stream(self, device: Device) -> Optional[AbstractSerialized]:
        """
        Defines how to the serial device will be read to decode the desired
        serialized object.
        """
        # Read until COBS end (0x00)
        recv = device.read_until(expected=b"\x00")
        if recv is None:
            raise ConnectionError(f"Connection error while reading from {device}")
        if len(recv) == 0:
            return None

        # Process
        return self._dtype.deserialize(data=COBS.decode(data=bytearray(recv)))
