#!/usr/bin/python
# -*- coding: ascii -*-
"""
Math utilities testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import unittest

from embutils.utils import closest_pow, closest_multi


# -->> Definitions <<------------------


# -->> Test API <<---------------------
class TestMath(unittest.TestCase):
    """
    Test math utilities.
    """
    def test_01_closest_multi(self):
        """
        Test closest multiple computation.
        """
        assert closest_multi(2, 2) == 2
        assert closest_multi(2, 2, True) == 4

    def test_02_closest_pow(self):
        """
        Test closest power computation.
        """
        assert closest_pow(0.1, 10) == 0.1
        assert closest_pow(0.1, 10, True) == 1


# -->> Test Execution <<---------------
if __name__ == '__main__':
    unittest.main()
