#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Consistent Overhead Byte Stuffing (COBS) implementation.

:date:      2024
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# --------------------------------------
__author__ = "Christian Wiche"
__version__ = "ALPHA"
# --------------------------------------

# Built-in
import dataclasses as dc
import typing as tp


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class COBS:
    """Consistent Overhead Byte Stuffing (COBS) encoding/decoding utilities"""

    STUFFING_BYTE: bytes = b"\x00"
    """COBS stuffing byte."""

    class DecodeException(Exception):
        """COBS decoding exception."""

    @dc.dataclass
    class Block:
        """COBS encoding block.

        :param code: Block code.
        :param data: Block data.
        :param zero: Requires zero ending.
        """

        code: int = dc.field()
        data: bytearray = dc.field()
        zero: bool = dc.field(default=False)

    @staticmethod
    def encode(
        data: tp.Union[bytes, bytearray] = bytearray(),
    ) -> bytearray:
        """Encodes a data buffer using COBS.

        :param data: Data to be encoded.

        :returns: Encoded data.
        """
        # Prepare
        blocks: tp.List[COBS.Block] = []
        base = bytearray(data.copy())
        base.append(0x00)
        # Encode
        while base:
            idx = base.find(0x00)
            code = (idx + 1) if (idx != -1) else len(base)
            if code > 0xFE:
                # Extended block:
                blocks.append(COBS.Block(code=0xFF, data=base[0:0xFE]))
                del base[0:0xFE]
            else:
                # Zero terminated block:
                blocks.append(COBS.Block(code=code, data=base[0 : (code - 1)]))
                del base[0:code]
        # Build
        out = bytearray()
        for block in blocks:
            out.append(block.code)
            out.extend(block.data)
        out.append(0x00)
        return out

    @staticmethod
    def decode(
        data: tp.Union[bytes, bytearray] = bytearray(),
    ) -> bytearray:
        """Decodes a data buffer using COBS.

        :param data: Data to be decoded.

        :returns: Decoded data.
        """
        # Prepare
        blocks: tp.List[COBS.Block] = []
        base = bytearray(data.copy())
        # Decode
        while base:
            # Check if termination byte is received
            code = base[0]
            if code == 0x00:
                break
            # Add a zero to the last block, if needed
            if blocks:
                blocks[-1].zero = blocks[-1].code != 0xFF
            # Get block and remove bytes
            block = COBS.Block(code=code, data=base[1:code])
            del base[0:code]
            # Check block
            if block.data.find(0x00) != -1:
                raise COBS.DecodeException("Zero byte found in input!")
            if len(block.data) != (block.code - 1):
                raise COBS.DecodeException("Block don't have enough bytes to be processed!")
            # Add block
            blocks.append(block)
        # Build
        out = bytearray()
        for block in blocks:
            out.extend(block.data)
            if block.zero:
                out.append(0x00)
        return out


# -->> API <<---------------------------


# -->> Export <<------------------------
__all__ = [
    "COBS",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
