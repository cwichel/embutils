#!/usr/bin/python
# -*- coding: ascii -*-
"""
COBS encoding utility.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""


class COBSError(Exception):
    pass


def cobs_encode(data: bytearray = bytearray()) -> bytearray:
    """Encode a byte array using Consistent Overhead Byte Stuffing (COBS).

    Note:
        - Empty arrays will be encoded to "0x01".
        - The final byte "0x00" is not added.

    Args:
        data (bytearray): Bytes to be encoded.

    Returns:
        bytearray: Encoded message.
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


def cobs_decode(data: bytearray) -> bytearray:
    """Decode a byte array using Consistent Overhead Byte Stuffing (COBS).

    Note:
        - The input dont need to include the last "0x00" byte.

    Args:
        data (bytearray): Bytes to be decoded.

    Returns:
        bytearray: Decoded message.
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
            raise COBSError('Zero byte found in input!')

        # Get the data
        idx += 1
        end = idx + code - 1

        tmp = data[idx:end]
        if 0x00 in tmp:
            raise COBSError('Zero byte found in input!')

        # Append it to the message
        msg += tmp

        # Update and check index
        idx = end
        if idx > len(data):
            raise COBSError('Not enough bytes to process!')

        elif idx < len(data):
            # In range, add zero if needed
            if code < 0xFF:
                msg.append(0x00)

        else:
            # All the bytes processed
            break

    return msg
