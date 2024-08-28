#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Alternative enumerations implementations test suite.

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
import enum as en
import unittest as ut

# External
from embutils.core import EnumUtils


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class EnumTestItem(EnumUtils, en.IntEnum):
    """Test enumeration."""

    A = 0
    B = 1


class EnumTestSuite(ut.TestCase):
    def test_hasValue(
        self,
    ) -> None:
        """Test the if the item has a value"""
        # Test valid cases
        self.assertTrue(EnumTestItem.has_value(value=0))
        self.assertTrue(EnumTestItem.has_value(value=1))
        self.assertTrue(EnumTestItem.has_value(value="A"))
        self.assertTrue(EnumTestItem.has_value(value="B"))
        self.assertTrue(EnumTestItem.has_value(value=EnumTestItem.A))
        self.assertTrue(EnumTestItem.has_value(value=EnumTestItem.B))
        # Test invalid cases
        self.assertFalse(EnumTestItem.has_value(value=2))
        self.assertFalse(EnumTestItem.has_value(value="C"))

    def test_getItemFromValue(
        self,
    ) -> None:
        """Test the from_value method."""

        class OtherEnum(en.IntEnum):
            """Other enumeration."""

            C = 2

        # Test valid cases
        self.assertEqual(EnumTestItem.from_value(value=0), EnumTestItem.A)
        self.assertEqual(EnumTestItem.from_value(value=1), EnumTestItem.B)
        self.assertEqual(EnumTestItem.from_value(value="A"), EnumTestItem.A)
        self.assertEqual(EnumTestItem.from_value(value="B"), EnumTestItem.B)
        self.assertEqual(EnumTestItem.from_value(value=EnumTestItem.A), EnumTestItem.A)
        self.assertEqual(EnumTestItem.from_value(value=EnumTestItem.B), EnumTestItem.B)
        # Test invalid cases
        self.assertIsNone(EnumTestItem.from_value(value=2))
        self.assertIsNone(EnumTestItem.from_value(value="C"))
        self.assertIsNone(EnumTestItem.from_value(value=OtherEnum.C))


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
