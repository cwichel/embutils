#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""COBS (Consistent Overhead Byte Stuffing) implementation.

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
import itertools as it
import typing as tp


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
COBS_MAX_BLOCK_SIZE: int = 0xFE
"""Maximum block size for COBS encoding."""


# -->> API <<---------------------------
def cobs_encoded_max_size(
    size: int,
) -> int:
    """Calculate the maximum size of the encoded data."""
    return (size + (size // COBS_MAX_BLOCK_SIZE) if (size != 0) else 0) + 2


def cobs_encode(
    data: tp.Union[bytes, bytearray],
) -> bytearray:
    """Encode data using COBS algorithm."""
    # Special case: empty buffer
    if len(data) == 0:
        return bytearray([0x01, 0x00])

    # General case
    code = 1
    code_idx = 0
    add_code = True
    encoded = bytearray([0x00])
    for byte in data:
        add_code = True
        if byte != 0x00:
            encoded.append(byte)
            code += 1
        if byte == 0x00 or code == (COBS_MAX_BLOCK_SIZE + 1):
            if code == (COBS_MAX_BLOCK_SIZE + 1):
                add_code = False
            encoded[code_idx] = code
            encoded.append(0x00)
            code_idx = len(encoded) - 1
            code = 1
    if add_code:
        encoded[code_idx] = code
    if encoded[-1] != 0x00:
        encoded.append(0x00)
    return encoded


def cobs_decode(
    data: tp.Union[bytes, bytearray],
) -> bytearray:
    """Decode data using COBS algorithm."""
    # Validate
    if len(data) < cobs_encoded_max_size(0) or data[-1] != 0x00:
        raise ValueError("Invalid COBS input.")

    # Decode
    code = 0xFF
    block = 0
    decoded = bytearray()
    remaining = len(data) - 1
    for byte in it.islice(data, remaining):
        if byte == 0x00:
            raise ValueError("Zero found in COBS data.")
        if block:
            decoded.append(byte)
        else:
            if code != 0xFF:
                decoded.append(0x00)
            block = code = byte
            if block > remaining:
                raise ValueError("Not enough bytes remaining.")
            if code == 0x00:
                break
        block -= 1
        remaining -= 1
    return decoded


# -->> Export <<------------------------
__all__ = [
    "cobs_encoded_max_size",
    "cobs_encode",
    "cobs_decode",
]

# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
