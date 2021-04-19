#!/usr/bin/python
# -*- coding: ascii -*-
"""
CRC implementation file.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

from typing import List
from embutils.utils.common.bytes import as_hex, bitmask, reverse_bits


class CRC:
    """Table driven CRC calculation.
    """
    def __init__(self,
                 name: str = "CRC16_CCITT_FALSE", size: int = 16,
                 poly: int = 0x1021, crc_init: int = 0xFFFF, xor_out: int = 0x0000,
                 rev_in: bool = False, rev_out: bool = False
                 ):
        """Class initialization.

        Notes:
            - For the moment this implementation don't support CRCs with size < 8bits
            - The CRC configuration values cant be changed after initialization.
            - The CRC configuration values will be adjusted to the selected width: CRC16 poly 0x101021 -> 0x1021.

        Args:
            name    (str) : Identification name.
            size    (int) : Size in bits.
            poly    (int) : Generator polynomial value.
            crc_init(int) : Value used to initialize the CRC value.
            xor_out (int) : Value to be xored to the CRC sum before being returned.
            rev_in  (bool): If true every input byte will be reversed before being feed to the calculation.
            rev_out (bool): If true the final CRC value will be reversed before being returned.
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
        self._table = self._gen_table()

    def __repr__(self) -> str:
        """Get the class representation string.

        Return:
            str: Class representation string.
        """
        msg = '<{}: name={}, size={}, poly={}, crc_in={}, xor_out={}, ref_in={}, ref_out={}>'.format(
            self.__class__.__name__, self.name, self.size,
            self.poly_hex, self.crc_init_hex, self.xor_out_hex,
            self.reverse_in, self.reverse_out
            )
        return msg

    # Properties ================================
    @property
    def name(self) -> str:
        """CRC name.

        Returns:
            str: CRC algorithm name.
        """
        return self._name

    @property
    def size(self) -> int:
        """CRC bit size.

        Returns:
            int: CRC size (in bits).
        """
        return self._size

    @property
    def poly(self) -> int:
        """CRC polynomial.

        Returns:
            int: CRC polynomial value.
        """
        return self._poly

    @property
    def poly_hex(self) -> str:
        """CRC polynomial value (as hex string).

        Returns:
            str: CRC polynomial value in hex.
        """
        return as_hex(data=self._poly, size=self._size)

    @property
    def xor_out(self) -> int:
        """CRC out XOR value.

        Returns:
            int: CRC output XOR value.
        """
        return self._xor_out

    @property
    def xor_out_hex(self) -> str:
        """CRC out XOR value (as hex string).

        Returns:
            str: CRC output XOR value in hex.
        """
        return as_hex(data=self._xor_out, size=self._size)

    @property
    def crc_init(self) -> int:
        """CRC initial sum value.

        Returns:
            int: CRC input value.
        """
        return self._crc_init

    @property
    def crc_init_hex(self) -> str:
        """CRC initial sum value (as hex string).

        Returns:
            str: CRC input value in hex.
        """
        return as_hex(data=self._crc_init, size=self._size)

    @property
    def reverse_in(self) -> bool:
        """Reverse input data bits.

        Returns:
            bool: True if the bits are being reversed.
        """
        return self._rev_in

    @property
    def reverse_out(self) -> bool:
        """Reverse CRC output bits.

        Returns:
            bool: True if the bits are being reversed.
        """
        return self._rev_out

    @property
    def lookup_table(self) -> List[int]:
        """Return the CRC lookup table.

        Returns:
            list: CRC lookup table.
        """
        return self._table

    # API =======================================
    def compute(self, data: bytearray, crc_init: int = None) -> int:
        """Compute the CRC of the given data.

        Args:
            data (bytearray): Bytes to compute the CRC over.
            crc_init (int): Alternative initial value.

        Returns:
            int: CRC value.
        """
        # Select the initial value
        crc_init = self._crc_init if crc_init is None else crc_init

        # Process depending on size
        if self._size >= 8:
            # Define required constants
            shift = self._size - 8

            # Set the initial value and iterate through bytes
            crc = crc_init
            for byte in data:
                # Get the byte (reverse if necessary)
                byte = reverse_bits(data=byte, size=8) if self._rev_in else byte
                # Get index and update CRC
                pos = 0xFF & ((crc >> shift) ^ byte)
                crc = self._mask & ((crc << 8) ^ self._table[pos])

        else:
            # Define required constants
            shift = 8 - self._size

            if self._rev_in:
                # Set the initial value and iterate through bytes
                crc = reverse_bits(data=crc_init, size=self._size)
                for byte in data:
                    # Get index and update CRC
                    pos = 0xFF & (crc ^ byte)
                    crc = self._mask & ((crc >> 8) ^ self._table[pos])
                # Adjust output value
                crc = reverse_bits(data=crc, size=self._size)

            else:
                # Set the initial value and iterate through bytes
                crc = crc_init << shift
                for byte in data:
                    # Get index and update CRC
                    pos = 0xFF & (crc ^ byte)
                    crc = (self._mask << shift) & ((crc << self._size) ^ (self._table[pos] << shift))
                # Adjust output value
                crc >>= shift

        # Prepare the final CRC value and apply XOR
        crc = reverse_bits(data=crc, size=self._size) if self._rev_out else crc
        return crc ^ self._xor_out

    # API Private ===============================
    def _gen_table(self) -> List[int]:
        """Generate the lookup table for fast CRC computation.

        Returns:
            List[int]: Table with 256 pre-computed CRC values.
        """
        # Generate the lookup table
        out = []
        if self._size >= 8:
            # Define required constants
            shift = self._size - 8
            check = bitmask(bit=(self._size - 1))

            # Iterate through all the table values
            for idx in range(256):
                # The current byte is the table index
                byte = idx << shift

                # Compute the CRC value
                for bit in range(8):
                    byte = ((byte << 1) ^ self._poly) if ((byte & check) != 0) else (byte << 1)

                # Store the value on the table
                out.append(self._mask & byte)

        else:
            # Define required constants
            shift = (8 - self._size)
            check = bitmask(bit=7)

            # Iterate through all the table values
            for idx in range(256):
                # The current byte is the table index
                byte = reverse_bits(data=idx, size=8) if self._rev_in else idx

                # Compute the CRC value
                for bit in range(8):
                    byte = ((byte << 1) ^ (self._poly << shift)) if ((byte & check) != 0) else (byte << 1)

                # Store the value on the table
                byte = (reverse_bits(data=(byte >> shift), size=self._size) << shift) if self._rev_in else byte
                out.append(self._mask & (byte >> shift))

        # Return the lookup table
        return out
