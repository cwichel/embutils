#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Bit manipulation utilities.

:date:      2024
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# --------------------------------------
__author__ = "Christian Wiche"
__version__ = "ALPHA"
# --------------------------------------


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------


# -->> API <<---------------------------
def bit(
    n: int,
    /,
) -> int:
    """Return a mask with the nth bit as 1.

    Examples::

        assert(bit(0) == 0b00000001)
        assert(bit(2) == 0b00000100)
        assert(bit(5) == 0b00100000)

    :param n: Bit index.

    :return: bitmask.
    """
    return 1 << n


def bit_mask(
    n: int,
    /,
) -> int:
    """Returns a mask with the first n bits set.

    Examples::

        assert(bit_mask(0) == 0b00000000)
        assert(bit_mask(2) == 0b00000011)
        assert(bit_mask(5) == 0b00011111)

    :param n: Bit index.

    :return: bitmask.
    """
    return bit(n) - 1


def bit_reverse(
    value: int,
    size: int = 0,
) -> int:
    """Reverse the bits of the input value.

    Examples::

        assert(reverse_bits(0b100101)    == 0b101001)
        assert(reverse_bits(0b100101, 8) == 0b10100100)
        assert(reverse_bits(0b100101, 4) == 0b1010)

    .. note::

        - If size is not specified, it computes the minimum number of bits.
        - If size is provided but is smaller than the minimum number of bits,
          value will be truncated and reversed.

    :param value: Value to be reversed.
    :param size: Size of the input in bits.

    :return: Reversed value.
    """
    size = size or value.bit_length()
    value &= bit_mask(size)
    return int(f"{value:0{size:d}b}"[::-1], base=2)


# -->> Export <<------------------------
__all__ = [
    "bit",
    "bit_mask",
    "bit_reverse",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
