#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Cyclic Redundancy Check (CRC) implementation.

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

# App
from .bytes import bit, bit_mask, bit_reverse


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
@dc.dataclass(frozen=True)
class CRC:
    """Generic table-driven CRC implementation.

    :param name: CRC name.
    :param size: CRC size in bits.
    :param poly: CRC polynomial.
    :param init: CRC initial value.
    :param rev_in: Reverse input bytes.
    :param rev_out: Reverse output bytes.
    :param xor_out: XOR output value.
    """

    name: str = dc.field(default="CRC16_CCITT_FALSE")
    size: int = dc.field(default=16)
    poly: int = dc.field(default=0x1021)
    init: int = dc.field(default=0xFFFF)
    rev_in: bool = dc.field(default=False)
    rev_out: bool = dc.field(default=False)
    xor_out: int = dc.field(default=0x0000)

    bitmask: int = dc.field(init=False, repr=False)
    table: tp.List[int] = dc.field(init=False, repr=False)

    def __post_init__(
        self,
    ) -> None:
        """Initialize the CRC settings."""
        # Disable frozen attributes to allow the initialization process
        frozen_setattr = CRC.__setattr__
        CRC.__setattr__ = object.__setattr__
        # Initialize members
        self.__setattr__("bitmask", bit_mask(self.size))
        self.__setattr__("poly", self.bitmask & self.poly)
        self.__setattr__("init", self.bitmask & self.init)
        self.__setattr__("xor_out", self.bitmask & self.xor_out)
        self.__setattr__("table", self._lookup_normal() if (self.size >= 8) else self._lookup_small())
        # Restore frozen attributes
        CRC.__setattr__ = frozen_setattr

    def __call__(
        self,
        data: tp.Union[bytes, bytearray],
        init: int = None,
    ) -> int:
        """Compute the CRC of a data buffer.

        :param data: Data to compute the CRC of.
        :param init: Initial CRC value. Overrides the default value.

        :return: CRC value.
        """
        crc = (self._compute_normal if (self.size >= 8) else self._compute_small)(data=data, init=init or self.init)
        crc = bit_reverse(value=crc, size=self.size) if self.rev_out else crc
        return crc ^ self.xor_out

    def _compute_normal(
        self,
        data: tp.Union[bytes, bytearray],
        init: int,
    ) -> int:
        """Compute the CRC of a data buffer using a table lookup for normal-sized poly (>= 8bit).

        :param data: Data to compute the CRC of.
        :param init: Initial CRC value.

        :return: CRC value.
        """
        crc = init
        shift = self.size - 8
        for byte in data:
            byte = bit_reverse(value=byte, size=8) if self.rev_in else byte
            crc = self.bitmask & ((crc << 8) ^ self.table[(0xFF & ((crc >> shift) ^ byte))])
        return crc

    def _compute_small(
        self,
        data: tp.Union[bytes, bytearray],
        init: int,
    ) -> int:
        """Compute the CRC of a data buffer using a table lookup for small-sized poly (< 8bit).

        :param data: Data to compute the CRC of.
        :param init: Initial CRC value.

        :return: CRC value.
        """
        shift = 8 - self.size
        if self.rev_in:
            crc = bit_reverse(value=init, size=self.size)
            for byte in data:
                crc = self.bitmask & ((crc >> 8) ^ self.table[0xFF & (crc ^ byte)])
            crc = bit_reverse(value=crc, size=self.size)
        else:
            crc = init << shift
            for byte in data:
                crc = (self.bitmask << shift) & ((crc << self.size) ^ (self.table[0xFF & (crc ^ byte)] << shift))
            crc >>= shift
        return crc

    def _lookup_normal(
        self,
    ) -> tp.List[int]:
        """Compute the CRC lookup table for normal-sized poly (>= 8bit).

        :return: CRC lookup table.
        """
        table = []
        shift = self.size - 8
        check = bit(self.size - 1)
        for idx in range(256):
            byte = idx << shift
            for _ in range(8):
                byte = ((byte << 1) ^ self.poly) if (byte & check) else (byte << 1)
            table.append(self.bitmask & byte)
        return table

    def _lookup_small(
        self,
    ) -> tp.List[int]:
        """Compute the CRC lookup table for small-sized poly (< 8bit).

        :return: CRC lookup table.
        """
        table = []
        shift = 8 - self.size
        check = bit(7)
        for idx in range(256):
            byte = bit_reverse(value=idx, size=8) if self.rev_in else idx
            for _ in range(8):
                byte = ((byte << 1) ^ (self.poly << shift)) if (byte & check) else (byte << 1)
            byte = (bit_reverse(value=(byte >> shift), size=self.size) << shift) if self.rev_in else byte
            table.append(self.bitmask & (byte >> shift))
        return table


# -->> API <<---------------------------


# -->> Export <<------------------------
__all__ = [
    "CRC",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
