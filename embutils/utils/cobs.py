#!/usr/bin/python
# -*- coding: ascii -*-
"""
COBS encoding/decoding implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import typing as tp

import attr


# -->> Definitions <<------------------


# -->> API <<--------------------------
class COBS:
    """
    Consistent Overhead Byte Stuffing (COBS) encoding/decoding utilities.
    """
    class DecodeException(Exception):
        """
        COBS decoding exception.
        """

    @attr.s
    class Block:
        """
        COBS encoding block.
        """
        #: Block code
        code: int       = attr.ib(converter=int)
        #: Block data array
        data: bytearray = attr.ib(converter=bytearray)
        #: Flag. Defines if is required to add a zero at the end.
        zero: bool      = attr.ib(converter=bool, default=False)

    @staticmethod
    def encode(data: bytearray = bytearray()) -> bytearray:
        """
        Encode a byte array using Consistent Overhead Byte Stuffing (COBS).

        .. note::
            * Encoding guarantees non-zero bytes on the output array (besides the terminator).
            * An empty string is encoded to [0x01, 0x00]

        :param bytearray data: Bytes to be encoded.

        :returns: Encoded byte array.
        :rtype: bytearray
        """
        # Prepare
        blocks: tp.List[COBS.Block] = []
        base = data.copy()
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
                # Block zero terminated:
                blocks.append(COBS.Block(code=code, data=base[0:(code - 1)]))
                del base[0:code]

        # Process encoding
        out = bytearray()
        for block in blocks:
            out.append(block.code)
            out.extend(block.data)
        out.append(0x00)
        return out

    @staticmethod
    def decode(data: bytearray) -> bytearray:
        """
        Decodes a byte array that was encoded using Consistent Overhead Byte
        Stuffing (COBS).

        :param bytearray data: Bytes to be decoded.

        :returns: Decoded byte array.
        :rtype: bytearray

        :raises COBS.DecodeException: Encoded data is invalid.
        """
        # Prepare
        blocks: tp.List[COBS.Block] = []
        base = data.copy()

        # Decode
        while base:
            # Check if the termination byte is received
            code = base[0]
            if code == 0x00:
                break
            # Add zero to last block, if needed
            if blocks:
                blocks[-1].zero = (blocks[-1].code != 0xFF)
            # Get block and remove bytes
            block = COBS.Block(code=code, data=base[1:code])
            del base[0:code]
            # Check block
            if block.data.find(0x00) != -1:
                raise COBS.DecodeException("Zero byte found in input!")
            if len(block.data) != (code - 1):
                raise COBS.DecodeException("Not enough bytes to process!")
            # Append block
            blocks.append(block)

        # Process decoding
        out = bytearray()
        for block in blocks:
            out.extend(block.data)
            if block.zero:
                out.append(0x00)
        return out
