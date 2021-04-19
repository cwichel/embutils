#!/usr/bin/python
# -*- coding: ascii -*-
"""
Byte-related utilities test file.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

import unittest
from embutils.utils.common import bitmask, reverse_bits, reverse_bytes


# Test Definitions ==============================
class TestByte(unittest.TestCase):
    """Check the byte utilities.
    """
    def test_bitmask(self):
        """Test if the bitmasks are being generated as expected:
            - bitmask (common): All zeroes but the bit index.
            - bitmask (fill): All ones from 0 to bit index.
        """
        mask_fill = bitmask(bit=7, fill=True)
        mask_bit = bitmask(bit=7)
        assert mask_fill == 0b11111111
        assert mask_bit == 0b10000000

    def test_reverse_bits(self):
        """Test if the bits are being reversed.
        """
        rev_bits = reverse_bits(data=0b00101011, size=8)
        assert rev_bits == 0b11010100

    def test_reverse_bytes(self):
        """Tests if the bytes are being reversed.
        """
        rev_bytes = reverse_bytes(data=bytearray([0x01, 0x02, 0x03, 0x04]))
        assert rev_bytes == bytearray([0x04, 0x03, 0x02, 0x01])


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
