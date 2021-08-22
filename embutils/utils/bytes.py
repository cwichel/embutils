#!/usr/bin/python
# -*- coding: ascii -*-
"""
Byte manipulation utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""


# -->> Definitions <<------------------


# -->> API <<--------------------------
def bitmask(bit: int, fill: bool = False) -> int:
    """
    Returns a bitmask for the given bit length.

    :param int bit:     Bit length.
    :param bool fill:   If true, fill the mask with ones.

    :returns: bitmask.
    :rtype: int
    """
    mask = (1 << bit)
    return (((mask - 1) << 1) | 1) if fill else mask


def reverse_bits(value: int, size: int = None) -> int:
    """
    Reverse the bits of the input value.

    :param int value:   Value to be reversed.
    :param int size:    Size of the input in bits. By default it computes the minimum number of bits.

    :returns: Reversed value.
    :rtype: int
    """
    if not size:
        size = value.bit_length()

    val = value & bitmask(bit=(size - 1), fill=True)
    aux = f'{val:0{size:d}b}'
    return int(aux[::-1], base=2)


def reverse_bytes(value: int, size: int = None) -> int:
    """
    Reverse the bytes of the input value.

    :param int value:   Value to be reversed.
    :param int size:    Size of the input in bytes. By default it computes the minimum number of bytes.

    :returns: Reversed value.
    :rtype: int
    """
    if not size:
        size = (value.bit_length() + 7) // 8 

    val = value & bitmask(bit=((8 * size) - 1), fill=True)
    aux = val.to_bytes(length=size, byteorder='big')
    return int.from_bytes(bytes=aux[::-1], byteorder='big')
