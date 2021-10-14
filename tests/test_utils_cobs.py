#!/usr/bin/python
# -*- coding: ascii -*-
"""
COBS encode/decode testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import pytest
import unittest

from embutils.utils import COBS


# -->> Definitions <<------------------


# -->> Test API <<---------------------
class TestCOBS(unittest.TestCase):
    """
    Test COBS utilities.
    """
    def test_01_fail(self):
        """
        Test COBS failure cases.
        """
        # Not enough data
        with pytest.raises(COBS.DecodeException):
            COBS.decode(data=bytearray([0x02]))

        # 0x00 found in the middle of a block
        with pytest.raises(COBS.DecodeException):
            COBS.decode(data=bytearray([0x02, 0x00, 0x01]))

    def test_02_wiki_examples(self):
        """
        Test based on COBS wikipedia page examples.

        .. note::
            Cases explored:
            * Zero data.
            * Normal messages.
            * Large messages.
            * Large messages with zero/short extensions.
        """
        # Prepare data
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
            [(n % (0xFF + 1)) for n in range(0x03, 0xFF + 0x03)]
            ]

        # Execute example tests
        for ex in data:
            assert self._test_base(data=bytearray(ex))

    def test_03_multi_blocks(self):
        """
        Test based on COBS paper: http://www.stuartcheshire.org/papers/COBSforToN.pdf

        .. note::
            Cases explored:
            * Long multi-block messages.
        """
        # Prepare data
        data = [n for n in range(0x01, 0xFF + 0x01)]
        data.extend(data)
        data.extend([0x01, 0x02, 0x03, 0x04])

        # Execute test
        assert self._test_base(data=bytearray(data))

    @staticmethod
    def _test_base(data: bytearray) -> bool:
        """
        COBS test structure definition.

        :param bytearray data: Data to test.

        :returns: True if succeed, false otherwise.
        :rtype: bool
        """
        # Encode / decode the data
        encode = COBS.encode(data=data)
        decode = COBS.decode(data=encode)

        # Perform the test
        return data == decode


# -->> Test Execution <<---------------
if __name__ == '__main__':
    unittest.main()
