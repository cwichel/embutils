#!/usr/bin/env python
##
# @file       bytes.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Byte manipulation utilities.
# =============================================================================

from math import ceil
from typing import Union


def bitmask(bit: int, fill: bool = False) -> int:
    """Return a bitmask.

    Args:
        bit (int): Bit position.
        fill (bool): Fill all the mask with ones.

    Return:
        int: bitmask.
    """
    mask = (1 << bit)
    return (((mask - 1) << 1) | 1) if fill else mask


def reverse_bits(data: int, size: int = 8) -> int:
    """Reverse the bits of the input data.
    Ex: b10000010 -> b01000001

    Args:
        data (int): Input byte.
        size (int): The size of the output in bits.

    Return:
        int: Reverser value.
    """
    data &= bitmask(bit=size - 1, fill=True)
    aux = '{data:0{size:d}b}'.format(data=data, size=size)
    return int(aux[::-1], base=2)


def reverse_bytes(data: bytearray) -> bytearray:
    """Return the reversed byte array

    Args:
        data (bytearray): Bytes to be reversed.

    Return:
         bytearray: Reversed bytes.
    """
    return data[::-1]


def as_bin(data: int, size: int = 8) -> str:
    """Return the input data as a BIN string.

    Note: The output will be truncated by the size.

    Args:
        data (int): Input value.
        size (int): Size in bits.

    Return:
        str: Binary string.
    """
    data &= bitmask(bit=size - 1, fill=True)
    return '0b{value:0{size:d}b}'.format(value=data, size=size)


def as_hex(data: Union[int, bytearray], size: int = 8) -> str:
    """Return the input data as a HEX string.

    Note: The output will be truncated by the size.

    Args:
        data (int): Input value.
        size (int): Size in bits.

    Return:
        str: Binary string.
    """
    if isinstance(data, bytearray):
        return '0x' + ''.join(['{byte:02X}'.format(byte=byte) for byte in data])

    else:
        data &= bitmask(bit=(size - 1), fill=True)
        return '0x{value:0{size:d}X}'.format(value=data, size=ceil(size / 4))
