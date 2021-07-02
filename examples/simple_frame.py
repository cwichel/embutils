#!/usr/bin/python
# -*- coding: ascii -*-
"""
Frame and frame handler implementation example.

To consider:
*   The frame contains the message structure.
*   The frame handler defines how to translate the bytes received by the serial
    device into a frame object.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from typing import Union
from dataclasses import dataclass
from embutils.serial.core import SerialDevice
from embutils.serial.data import Frame, FrameHandler
from embutils.utils import CRC, COBS, EventHook, ThreadItem


@dataclass
class SimpleFrame(Frame):
    """
    Simple frame implementation.

    On this example the frame structure is:

    #. Source ID:        uint8_t
    #. Destination ID:   uint8_t
    #. Length:           uint8_t
    #. Payload:          length * uint_8
    #. CRC16:            uint16_t

    """
    CRC16 = CRC()

    source:         int
    destination:    int
    payload:        bytearray

    @property
    def crc(self) -> int:
        """
        Get the frame CRC value.

        :returns: Frame CRC.
        :rtype: int
        """
        return self.CRC16.compute(data=self._base())

    @property
    def length(self) -> int:
        """
        Get the frame payload length.

        :returns: payload length.
        :rtype: int
        """
        return len(self.payload)

    def raw(self) -> bytearray:
        """
        Frame base bytes with CRC included.

        :returns: Raw frame bytes.
        :rtype: bytearray
        """
        return bytearray(
            self._base() +
            self.crc.to_bytes(length=2, byteorder='little', signed=False)
            )

    def _base(self) -> bytearray:
        """
        Frame base bytes. This don't include the CRC value.

        :returns: Base frame bytes.
        :rtype: bytearray
        """
        return bytearray(
            bytes([self.source, self.destination, self.length]) +
            self.payload
            )

    def serialize(self) -> bytearray:
        """
        Serialize the frame into bytes.

        On this example we:

        #. Convert the frame to bytes (including CRC).
        #. Apply COBS encoding.

        :returns: Serialized frame.
        :rtype: bytearray
        """
        return COBS.encode(data=self.raw())

    @staticmethod
    def deserialize(data: bytearray) -> Union[None, 'SimpleFrame']:
        """
        Deserialize the frame from incoming bytes.

        On this example:

        #. Decode input using COBS.
        #. Parse the frame components from the decoded bytes.
        #. Compare generated frame CRC with the one obtained form parsing.

        :returns: None if the deserialization fails, a frame otherwise.
        :rtype: Union[None, SimpleFrame]
        """
        dec_data = COBS.decode(data=data)
        data_len = dec_data[2]
        frame_crc = int.from_bytes(bytes=dec_data[-2:], byteorder='little', signed=False)
        frame = SimpleFrame(
            source=dec_data[0],
            destination=dec_data[1],
            payload=dec_data[3:-2],
            )
        if (frame.crc == frame_crc) and (frame.length == data_len):
            return frame
        return None


class SimpleFrameHandler(FrameHandler):
    """
    Simple frame handler implementation.

    The target of this class is to define how to read the input bytes to
    deserialize a frame from the input.
    """
    def read_process(self, serial: SerialDevice, emitter: EventHook) -> bool:
        """
        In this read process we are trying to recover a COBS encoded message
        so we need to:

        #. Read bytes until 0x00 is detected (COBS ending byte).
        #. Try to deserialize (parse) the frame from received bytes.

        :param SerialDevice serial: Serial device from where the bytes are read.
        :param EventHook emitter:   Event to be raised when a frame is received.

        :returns: True if success, false on serial device disconnection or reading issues.
        :rtype: bool
        """
        # Wait until a byte is received
        recv = serial.read(size=1)
        if recv is None:
            # Device failure / disconnection
            return False
        if len(recv) == 0:
            # Data not available yet...
            return True

        # Check value
        byte = ord(recv)
        if byte != 0x00:
            # Byte not stuff... frame incoming
            raw_frame = bytearray(recv)

            # Receive the rest...
            recv = serial.read_until(expected=b'\x00')
            raw_frame.extend(recv)
            if len(raw_frame) > 1:
                frame = SimpleFrame.deserialize(data=raw_frame)
                if frame is not None:
                    ThreadItem(name=f'{self.__class__.__name__}: Frame received', target=lambda: emitter.emit(frame=frame))

        # Process without issues
        return True
