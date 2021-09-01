#!/usr/bin/python
# -*- coding: ascii -*-
"""
COBS encoding/decoding implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""


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
        pass

    @staticmethod
    def encode(data: bytearray = bytearray()) -> bytearray:
        """
        Encode a byte array using Consistent Overhead Byte Stuffing (COBS).

        .. note::
            * Encoding guarantees non-zero bytes on the output array.
            * An empty string is encoded to [0x01]

        :param bytearray data: Bytes to be encoded.

        :returns: Encoded byte array.
        :rtype: bytearray
        """
        # Verify that we have bytes to encode...
        if len(data) == 0:
            return bytearray([0x01])

        # Encode
        frame = bytearray()
        add_zero = False
        idx_start = 0
        idx_end = 0
        for byte in data:
            # Compute code
            code = idx_end - idx_start + 1

            # Process the current byte
            if byte == 0x00:
                # Add a zero: Block termination
                #   - If this is the last message: Add another zero to show that is ready!
                #   - We need to append < 0xFE bytes!
                #   - Append the code (bytes available).
                add_zero = True
                frame.append(code)
                frame += data[idx_start:idx_end]
                idx_start = idx_end + 1

            elif code == 0xFE:
                # Special case: Send the full block with non-zero bytes
                #   - We have 0xFE bytes available!
                #   - The block header is set to 0xFF
                #   - Don't need to add a zero termination!
                add_zero = False
                frame.append(0xFF)
                frame += data[idx_start:(idx_end + 1)]
                idx_start = idx_end + 1

            # Explore the next byte...
            idx_end += 1

        # Finish the packet:
        if (idx_end != idx_start) or add_zero:
            # If needed:
            #   - Add the block header code (if no bytes missing: 0x01)
            #   - Add the missing bytes
            code = idx_end - idx_start + 1
            frame.append(code)
            frame += data[idx_start:idx_end]

        return frame

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
        # Verify that he have enough bytes
        if len(data) == 0:
            return bytearray()

        msg = bytearray()
        idx = 0

        while idx < len(data):
            # Get the frame block code
            code = data[idx]
            if code == 0x00:
                raise COBS.DecodeException('Zero byte found in input!')

            # Get the data
            idx += 1
            end = idx + code - 1

            tmp = data[idx:end]
            if 0x00 in tmp:
                raise COBS.DecodeException('Zero byte found in input!')

            # Append it to the message
            msg += tmp

            # Update and check index
            idx = end
            if idx > len(data):
                raise COBS.DecodeException('Not enough bytes to process!')

            if idx < len(data):
                # In range, add zero if needed
                if code < 0xFF:
                    msg.append(0x00)

            else:
                # All the bytes processed
                break

        return msg
