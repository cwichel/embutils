#!/usr/bin/python
# -*- coding: ascii -*-
"""
Byte utilities testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import unittest
from embutils.utils import bitmask, reverse_bits, reverse_bytes


# Test Definitions ==============================
class TestBytes(unittest.TestCase):
    """
    Test byte utilities.
    """
    def test_01_bitmask(self):
        """
        Test bitmask generation.
        """
        # Test bitmask fill
        mask = bitmask(bit=7, fill=True)
        assert mask == 0b11111111

        # Test bitmask
        mask = bitmask(bit=7)
        assert mask == 0b10000000

    def test_02_reverse_bits(self):
        """
        Test bits reverse.
        """
        # Test using fixed size
        rev_bits = reverse_bits(value=0b00101011, size=8)
        assert rev_bits == 0b11010100

        # Test using minimum size
        rev_bits = reverse_bits(value=0b00101011)
        assert rev_bits == 0b110101

    def test_03_reverse_bytes(self):
        """
        Test bytes reverse.
        """
        # Test using fixed size
        rev_bytes = reverse_bytes(value=0x00020304, size=4)
        assert rev_bytes == 0x04030200

        # Test using minimum size
        rev_bytes = reverse_bytes(value=0x00020304)
        assert rev_bytes == 0x040302


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
