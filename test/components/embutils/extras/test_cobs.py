#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Cyclic Redundancy Check (CRC) implementation test suite.

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
from embutils.extras import COBS


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class COBSTestSuite(ut.TestCase):
    def test_failureScenarios(
        self,
    ) -> None:
        """Test COBS failure scenarios."""
        # Not enough data
        with self.assertRaises(COBS.DecodeException):
            COBS.decode(data=bytearray([0x02]))
        # Zero found in data
        with self.assertRaises(COBS.DecodeException):
            COBS.decode(data=bytearray([0x02, 0x00, 0x01]))

    def test_encodeDecodeMultiBlock(
        self,
    ) -> None:
        """Test COBS encoding/decoding using large data blocks."""
        # Prepare
        data = bytearray([idx for idx in range(0x01, 0xFF + 0x01)])
        data.extend(data)
        data.extend([0x01, 0x02, 0x03, 0x04])
        # Run
        self._run_test(data=data)

    def test_encodeDecodeWikipedia(
        self,
    ) -> None:
        """Test COBS encoding/decoding using Wikipedia examples."""
        # Prepare
        data = [
            [],
            [0x00],
            [0x00, 0x00],
            [0x11, 0x22, 0x00, 0x33],
            [0x11, 0x22, 0x33, 0x44],
            [0x11, 0x00, 0x00, 0x00],
            [n for n in range(0x01, 0xFF)],
            [n for n in range(0x00, 0xFF)],
            [(n % (0xFF + 1)) for n in range(0x01, 0xFF + 0x01)],
            [(n % (0xFF + 1)) for n in range(0x02, 0xFF + 0x02)],
            [(n % (0xFF + 1)) for n in range(0x03, 0xFF + 0x03)],
        ]
        # Run
        for item in data:
            self._run_test(data=bytearray(item))

    def _run_test(
        self,
        data: bytearray,
    ) -> None:
        """Run a COBS test."""
        encoded = COBS.encode(data=data)
        decoded = COBS.decode(data=encoded)
        self.assertEqual(data, decoded)


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
