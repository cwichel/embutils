#!/usr/bin/python
# -*- coding: ascii -*-
"""
Version implementation testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import pytest
import unittest

from embutils.utils import Version


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class TestVersion(unittest.TestCase):
    """
    Test version implementation.
    """
    def test_01_parse_fail_type(self):
        """
        Version parsing failure.
        """
        # Define error cases
        tests = [
            None, 1, 1.0,
            "", "1", "1.0",
            ]

        # Execute tests
        for item in tests:
            with pytest.raises(ValueError):
                Version.from_str(text=item)

    def test_02_parse_success(self):
        """
        Version parsing success.
        """
        # Define success cases
        tests = [
            ["99.0.abcd",       True,   "99.0.abcd"],
            ["99.0.1234",       False,  "99.0.1234"],
            ["99.0.X",          False,  "99.0.0"],
            ["99.0.X",          True,   "99.0.0"]
            ]

        # Execute tests
        for item in tests:
            assert f"{Version.from_str(text=item[0], hex_build=item[1])}" == item[2]


# -->> Execute <<----------------------
if __name__ == '__main__':
    unittest.main()
