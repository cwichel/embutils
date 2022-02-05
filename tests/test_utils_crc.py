#!/usr/bin/python
# -*- coding: ascii -*-
"""
CRC computation testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import unittest

from embutils.utils import ENCODE, CRC


# -->> Definitions <<------------------


# -->> Test API <<---------------------
class TestCRC(unittest.TestCase):
    """
    Test CRC computation utility.
    """
    #: Test data
    TEST_DATA = bytearray('123456789', encoding=ENCODE)

    def test_01_crc(self):
        """
        Test CRC calculation for several models.

        .. note::
            Models tested:
            * CRC-4/ITU
            * CRC-5/EPC
            * CRC-5/USB
            * CRC-8
            * CRC-8/EBU
            * CRC-16/CCIT-FALSE
            * CRC-16/MAXIM
            * CRC-32
            * CRC-32/POSIX
        """
        # Add elements to the test
        tests = [
            {
                "crc": CRC(
                    name='CRC-4/ITU', size=4, poly=0x03,
                    crc_init=0x00, xor_out=0x00,
                    rev_in=True, rev_out=True
                    ),
                "exp": 0x07
            },
            {
                "crc": CRC(
                    name='CRC-5/EPC', size=5, poly=0x09,
                    crc_init=0x09, xor_out=0x00
                    ),
                "exp": 0x00
            },
            {
                "crc": CRC(
                    name='CRC-5/USB', size=5, poly=0x05,
                    crc_init=0x1F, xor_out=0x1F,
                    rev_in=True, rev_out=True
                    ),
                "exp": 0x19
            },
            {
                "crc": CRC(
                    name='CRC-8', size=8, poly=0x07,
                    crc_init=0x00, xor_out=0x00
                    ),
                "exp": 0xF4
            },
            {
                "crc": CRC(
                    name='CRC-8/EBU', size=8, poly=0x1D,
                    crc_init=0xFF, xor_out=0x00,
                    rev_in=True, rev_out=True
                    ),
                "exp": 0x97
            },
            {
                "crc": CRC(
                    name='CRC-16/CCIT-FALSE', size=16,
                    poly=0x1021, crc_init=0xFFFF,
                    xor_out=0x0000
                    ),
                "exp": 0x29B1
            },
            {
                "crc": CRC(
                    name='CRC-16/MAXIM', size=16, poly=0x8005,
                    crc_init=0x0000, xor_out=0xFFFF,
                    rev_in=True, rev_out=True
                    ),
                "exp": 0x44C2
            },
            {
                "crc": CRC(
                    name='CRC-32', size=32, poly=0x04C11DB7,
                    crc_init=0xFFFFFFFF, xor_out=0xFFFFFFFF,
                    rev_in=True, rev_out=True
                    ),
                "exp": 0xCBF43926
            },
            {
                "crc": CRC(
                    name='CRC-32/POSIX', size=32, poly=0x04C11DB7,
                    crc_init=0x00000000, xor_out=0xFFFFFFFF
                    ),
                "exp": 0x765E7680
            }
        ]

        # Perform actual testing
        for test in tests:
            val = test["crc"].compute(data=self.TEST_DATA)
            assert test["exp"] == val


# -->> Test Execution <<---------------
if __name__ == '__main__':
    unittest.main()
