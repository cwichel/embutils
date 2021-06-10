#!/usr/bin/python
# -*- coding: ascii -*-
"""
COBS implementation testing.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

import unittest
from embutils.utils import COBS


# Test Definitions ==============================
class TestByte(unittest.TestCase):
    """Checks COBS utility.
    """
    def test_01_wiki_examples(self):
        """Test made using the wikipedia COBS page examples.
        Cases explored:
        - Normal messages.
        - Pure zeroes message.
        - Large messages.
        - Large messages with zero/short extensions.
        """
        # Prepare data
        data = [
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

        # Execute example
        print('--->> Test: Wiki Examples <<-----------------')
        idx = 0
        for ex in data:
            ex = bytearray(ex)
            ok = self._test_base(data=ex)
            print('> Example {}: {}'.format(idx, 'Passed!' if ok else 'Failed!'))
            assert ok
            idx += 1
        print()

    def test_02_multi_blocks(self):
        """Test based on COBS paper: http://www.stuartcheshire.org/papers/COBSforToN.pdf
        Case explored:
        - Long multi-block messages.
        """
        # Prepare data
        data = [n for n in range(0x01, 0xFF + 0x01)]
        data.extend(data)
        data.extend([0x01, 0x02, 0x03, 0x04])

        # Execute example
        print('--->> Test: Long Message <<------------------')
        ex = bytearray(data)
        ok = self._test_base(data=ex)
        print('> Status: {}'.format('Passed!' if ok else 'Failed!'))
        assert ok
        print()

    @staticmethod
    def _test_base(data: bytearray) -> bool:
        """Test structure definition.

        Args:
            data (bytearray): Data to be tested.

        Return:
            bool: Test result. True if success, false otherwise.
        """
        # Encode / decode the data
        encode = COBS.encode(data=data)
        decode = COBS.decode(data=encode)

        # Perform the test
        return data == decode


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
