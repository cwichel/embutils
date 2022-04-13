#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
CRC implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import typing as tp

from .bytes import bitmask, reverse_bits


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class CRC:
    """
    Generalized table-driven CRC implementation.

    .. note::
        *   The CRC model definitions can't be changed after initialization.
        *   The CRC configuration values will be adjusted to the defined bit
            size.

    """
    def __init__(self,
                 name: str = "CRC16_CCITT_FALSE", size: int = 16,
                 poly: int = 0x1021, crc_init: int = 0xFFFF, xor_out: int = 0x0000,
                 rev_in: bool = False, rev_out: bool = False
                 ):
        """
        CRC model initialization.

        :param str name:        Model name.
        :param int size:        Size of the CRC in bits.
        :param int poly:        Polynomial generator value.
        :param int crc_init:    Initial value.
        :param int xor_out:     Value to XOR with the CRC result before being returned.
        :param bool rev_in:     If true every input byte will be reversed before being feed to the calculation.
        :param bool rev_out:    If true the final CRC value will be reversed before being returned.
        """
        # Store configurations...
        self._name = name
        self._size = size
        self._rev_in = rev_in
        self._rev_out = rev_out

        # Adjust the values using a bitmask
        self._mask = bitmask(bit=(size - 1), fill=True)
        self._poly = self._mask & poly
        self._xor_out = self._mask & xor_out
        self._crc_init = self._mask & crc_init

        # Generate the lookup table
        self._table = self._compute_lookup_table()

    def __repr__(self) -> str:
        """
        Representation string.
        """
        size = 2 * ((self._size + 7) // 8)
        msg = f"{self.__class__.__name__}(name={self._name}, size={self._size}, " \
              f"poly=0x{self._poly:0{size:d}X}, " \
              f"crc_in=0x{self._crc_init:0{size:d}X}, " \
              f"xor_out=0x{self._xor_out:0{size:d}X}, " \
              f"ref_in={self._rev_in}, ref_out={self._rev_out})"
        return msg

    # Read only properties
    @property
    def name(self) -> str:
        """
        Model name.
        """
        return self._name

    @property
    def size(self) -> int:
        """
        Model bit size.
        """
        return self._size

    @property
    def poly(self) -> int:
        """
        Model polynomial.
        """
        return self._poly

    @property
    def xor_out(self) -> int:
        """
        Model output XOR value.
        """
        return self._xor_out

    @property
    def crc_init(self) -> int:
        """
        Model initial value.
        """
        return self._crc_init

    @property
    def reverse_in(self) -> bool:
        """
        Model input bit reverse flag.
        """
        return self._rev_in

    @property
    def reverse_out(self) -> bool:
        """
        Model output bit reverse flag.
        """
        return self._rev_out

    @property
    def lookup_table(self) -> tp.List[int]:
        """
        Model pre-computed lookup table.
        """
        return self._table

    def compute(self, data: bytearray, crc_init: int = None) -> int:
        """
        Computes the CRC for the given bytearray.

        :param bytearray data:  Data to compute the CRC over.
        :param int crc_init:    Overrides the default initial CRC value.
            You can use this parameter to perform chained CRC calculations over data blocks.

        :returns: CRC value.
        :rtype: int
        """
        # Select the initial value
        crc_init = self._crc_init if crc_init is None else crc_init

        # Process depending on size
        if self._size >= 8:
            crc = self._compute_normal(data=data, crc_init=crc_init)
        else:
            crc = self._compute_small(data=data, crc_init=crc_init)

        # Prepare the final CRC value and apply XOR
        crc = reverse_bits(value=crc, size=self._size) if self._rev_out else crc
        return crc ^ self._xor_out

    def _compute_lookup_table(self) -> tp.List[int]:
        """
        Generates the lookup table for the current CRC model.

        :returns: Table with 256 pre-computed CRC values.
        :rtype: List[int]
        """
        # Generate the lookup table
        if self._size >= 8:
            return self._lookup_normal()
        return self._lookup_small()

    def _compute_small(self, data: bytearray, crc_init: int) -> int:
        """
        Computes the CRC for model size < 8bit.

        :param bytearray data:  Data to compute the CRC over.
        :param int crc_init:    Overrides the default initial CRC value.

        :returns: CRC value.
        :rtype: int
        """
        # Define required constants
        shift = 8 - self._size
        if self._rev_in:
            # Set the initial value and iterate through bytes
            crc = reverse_bits(value=crc_init, size=self._size)
            for byte in data:
                # Get index and update CRC
                pos = 0xFF & (crc ^ byte)
                crc = self._mask & ((crc >> 8) ^ self._table[pos])
            # Adjust output value
            crc = reverse_bits(value=crc, size=self._size)
        else:
            # Set the initial value and iterate through bytes
            crc = crc_init << shift
            for byte in data:
                # Get index and update CRC
                pos = 0xFF & (crc ^ byte)
                crc = (self._mask << shift) & ((crc << self._size) ^ (self._table[pos] << shift))
            # Adjust output value
            crc >>= shift
        return crc

    def _lookup_small(self) -> tp.List[int]:
        """
        Generates the lookup table for model size < 8bit.

        :returns: Table with 256 pre-computed CRC values.
        :rtype: List[int]
        """
        out = []
        # Define required constants
        shift = (8 - self._size)
        check = bitmask(bit=7)

        # Iterate through all the table values
        for idx in range(256):
            # The current byte is the table index
            byte = reverse_bits(value=idx, size=8) if self._rev_in else idx

            # Compute the CRC value
            for _ in range(8):
                byte = ((byte << 1) ^ (self._poly << shift)) if ((byte & check) != 0) else (byte << 1)

            # Store the value on the table
            byte = (reverse_bits(value=(byte >> shift), size=self._size) << shift) if self._rev_in else byte
            out.append(self._mask & (byte >> shift))
        return out

    def _compute_normal(self, data: bytearray, crc_init: int) -> int:
        """
        Computes the CRC for model size >= 8bit.

        :param bytearray data:  Data to compute the CRC over.
        :param int crc_init:    Overrides the default initial CRC value.

        :returns: CRC value.
        :rtype: int
        """
        # Define required constants
        shift = self._size - 8
        # Set the initial value and iterate through bytes
        crc = crc_init
        for byte in data:
            # Get the byte (reverse if necessary)
            byte = reverse_bits(value=byte, size=8) if self._rev_in else byte
            # Get index and update CRC
            pos = 0xFF & ((crc >> shift) ^ byte)
            crc = self._mask & ((crc << 8) ^ self._table[pos])
        return crc

    def _lookup_normal(self) -> tp.List[int]:
        """
        Generates the lookup table for model size >= 8bit.

        :returns: Table with 256 pre-computed CRC values.
        :rtype: List[int]
        """
        out = []
        # Define required constants
        shift = self._size - 8
        check = bitmask(bit=(self._size - 1))

        # Iterate through all the table values
        for idx in range(256):
            # The current byte is the table index
            byte = idx << shift

            # Compute the CRC value
            for _ in range(8):
                byte = ((byte << 1) ^ self._poly) if ((byte & check) != 0) else (byte << 1)

            # Store the value on the table
            out.append(self._mask & byte)
        return out


# -->> Export <<-----------------------
__all__ = [
    "CRC",
    ]
