#!/usr/bin/env python
##
# @file       ex_frame.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Example on frame and frame handler creation.
# =============================================================================

from typing import Union
from embutils.serial_process.data import Frame
from embutils.utils.check import CRC
from embutils.utils.framing import cobs_encode, cobs_decode


class SimpleFrame(Frame):
    """Implementation of a simple frame.
    This frame includes:
        - Source ID:        uint8_t
        - Destination ID:   uint8_t
        - Length:           uint8_t
        - Payload:          length * uint_8
        - CRC16:            uint16_t
    """
    CRC16 = CRC()

    def __init__(self, source: int, destination: int, payload: bytearray):
        self._src = 0xFF & source
        self._dst = 0xFF & destination
        self._ply = payload

    @property
    def crc(self) -> int:
        return self.CRC16.compute(data=self._base())

    @property
    def length(self) -> int:
        return len(self._ply)

    @property
    def source(self) -> int:
        return self._src

    @source.setter
    def source(self, value: int) -> None:
        self._src = 0xFF & value

    @property
    def destination(self) -> int:
        return self._dst

    @destination.setter
    def destination(self, value) -> None:
        self._dst = 0xFF & value

    @property
    def payload(self) -> bytearray:
        return self._ply

    @payload.setter
    def payload(self, data: bytearray) -> None:
        self._ply = data

    def _raw(self) -> bytearray:
        return bytearray(
            self._base() +
            self.crc.to_bytes(length=2, byteorder='little', signed=False)
            )

    def _base(self) -> bytearray:
        return bytearray(bytes([self.source, self.destination, self.length]) + self.payload)

    def serialize(self) -> bytearray:
        return cobs_encode(data=self._raw())

    @staticmethod
    def deserialize(data: bytearray) -> Union[None, 'SimpleFrame']:
        dec_data = cobs_decode(data=data)
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


class FrameHandler