#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Bit manipulation utilities test suite.

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
import unittest as ut

# External
from embutils.core import bit, bit_mask, bit_reverse


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class BytesTestSuite(ut.TestCase):
    def test_bit(
        self,
    ) -> None:
        """Test bit manipulation."""
        self.assertEqual(bit(0), 0b00000001)
        self.assertEqual(bit(2), 0b00000100)
        self.assertEqual(bit(5), 0b00100000)

    def test_bitMask(
        self,
    ) -> None:
        """Test bitmask manipulation."""
        self.assertEqual(bit_mask(0), 0b00000000)
        self.assertEqual(bit_mask(2), 0b00000011)
        self.assertEqual(bit_mask(5), 0b00011111)

    def test_bitReverse(
        self,
    ) -> None:
        """Test reverse bits."""
        self.assertEqual(bit_reverse(0b100101), 0b101001)
        self.assertEqual(bit_reverse(0b100101, 4), 0b1010)
        self.assertEqual(bit_reverse(0b100101, 8), 0b10100100)


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
