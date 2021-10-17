#!/usr/bin/python
# -*- coding: ascii -*-
"""
Enumeration testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import pytest
import unittest

from embutils.utils import IntEnum


# -->> Definitions <<------------------
class EnumExample(IntEnum):
    """
    Simple enumeration example
    """
    ONE     = 1
    TWO     = 2
    THREE   = 3


# -->> Test API <<---------------------
class TestEnum(unittest.TestCase):
    """
    Test Enum utility.
    """
    def test_01_check_value(self):
        """
        Test enum value check.
        """
        assert EnumExample.has_value(value=1)
        assert not EnumExample.has_value(value=4)

    def test_02_from_int(self):
        """
        Test enum from int functionality.
        """
        # Exception when a not existing value is provided
        with pytest.raises(ValueError):
            EnumExample.from_int(value=6)

        # Should return matching item
        assert EnumExample.from_int(value=3) == EnumExample.THREE


# -->> Test Execution <<---------------
if __name__ == '__main__':
    unittest.main()
