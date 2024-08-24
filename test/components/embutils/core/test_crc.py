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
import dataclasses as dc
import unittest as ut

# External
from embutils.core import CRC


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
@dc.dataclass
class CRCTestItem:
    algo: CRC
    data: bytearray
    result: int


class CRCTestSuite(ut.TestCase):
    def test_compute(
        self,
    ) -> None:
        """Test CRC computation."""
        data = bytearray("123456789", encoding="utf-8")
        tests = [
            CRCTestItem(
                algo=CRC(
                    name="CRC-4/ITU",
                    size=4,
                    poly=0x03,
                    init=0x00,
                    xor_out=0x00,
                    rev_in=True,
                    rev_out=True,
                ),
                data=data,
                result=0x07,
            ),
            CRCTestItem(
                algo=CRC(
                    name="CRC-5/EPC",
                    size=5,
                    poly=0x09,
                    init=0x09,
                    xor_out=0x00,
                    rev_in=False,
                    rev_out=False,
                ),
                data=data,
                result=0x00,
            ),
            CRCTestItem(
                algo=CRC(
                    name="CRC-5/USB",
                    size=5,
                    poly=0x05,
                    init=0x1F,
                    xor_out=0x1F,
                    rev_in=True,
                    rev_out=True,
                ),
                data=data,
                result=0x19,
            ),
            CRCTestItem(
                algo=CRC(
                    name="CRC-8",
                    size=8,
                    poly=0x07,
                    init=0x00,
                    xor_out=0x00,
                    rev_in=False,
                    rev_out=False,
                ),
                data=data,
                result=0xF4,
            ),
            CRCTestItem(
                algo=CRC(
                    name="CRC-8/EBU",
                    size=8,
                    poly=0x1D,
                    init=0xFF,
                    xor_out=0x00,
                    rev_in=True,
                    rev_out=True,
                ),
                data=data,
                result=0x97,
            ),
            CRCTestItem(
                algo=CRC(
                    name="CRC-16/CCIT-FALSE",
                    size=16,
                    poly=0x1021,
                    init=0xFFFF,
                    xor_out=0x0000,
                    rev_in=False,
                    rev_out=False,
                ),
                data=data,
                result=0x29B1,
            ),
            CRCTestItem(
                algo=CRC(
                    name="CRC-16/CCIT-MAXIM",
                    size=16,
                    poly=0x8005,
                    init=0x0000,
                    xor_out=0xFFFF,
                    rev_in=True,
                    rev_out=True,
                ),
                data=data,
                result=0x44C2,
            ),
            CRCTestItem(
                algo=CRC(
                    name="CRC-32",
                    size=32,
                    poly=0x04C11DB7,
                    init=0xFFFFFFFF,
                    xor_out=0xFFFFFFFF,
                    rev_in=True,
                    rev_out=True,
                ),
                data=data,
                result=0xCBF43926,
            ),
            CRCTestItem(
                algo=CRC(
                    name="CRC-32/POSIX",
                    size=32,
                    poly=0x04C11DB7,
                    init=0x00000000,
                    xor_out=0xFFFFFFFF,
                    rev_in=False,
                    rev_out=False,
                ),
                data=data,
                result=0x765E7680,
            ),
            CRCTestItem(
                algo=CRC(
                    name="CRC-32/STM32",
                    size=32,
                    poly=0x04C11DB7,
                    init=0xFFFFFFFF,
                    xor_out=0x00000000,
                    rev_in=False,
                    rev_out=False,
                ),
                data=data,
                result=0x0376E6E7,
            ),
        ]
        # Run tests
        for test in tests:
            crc = test.algo(data=test.data)
            self.assertEqual(crc, test.result)


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
