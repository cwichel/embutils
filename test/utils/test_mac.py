#!/usr/bin/env python
##
# @file       test_mac.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Test for MAC implementation.
# =============================================================================


import unittest
from embutils.utils.common import MacAddress, reverse_bytes


# Test Definitions ==============================
class TestByte(unittest.TestCase):
    """Check the MAC implementation.
    """
    def test_mac_initialize(self):
        t1 = MacAddress(value='12:34:56:78:9A:BC', byteorder='little')
        t2 = MacAddress(value=bytearray([0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC]), byteorder='big')
        t3 = MacAddress(value=['12', '34', '56', '78', '9A', 'BC'], byteorder='big')
        t4 = MacAddress(value=20015998343868, byteorder='big')
        assert t1.value == t2.value == t3.value == t4.value

    def test_mac_endianness(self):
        test = MacAddress(value='12:34:56:78:9A:BC', byteorder='little')
        data = test.as_bytes
        assert test.as_int == 0x123456789ABC

        test.byteorder = 'big'
        assert test.as_bytes == reverse_bytes(data)


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
