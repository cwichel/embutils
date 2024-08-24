#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Alternative dictionaries implementations test suite.

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
from embutils.core import DictAlias


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class DictAliasTestSuite(ut.TestCase):
    def setUp(
        self,
    ) -> None:
        """Set up the test suite."""
        self.dict = DictAlias()
        self.dict["key"] = "value"
        self.dict.set_alias(key="key", alias="alias")

    def test_keyValueEqualToAliasValue(
        self,
    ) -> None:
        """Test key and alias."""
        self.assertTrue(len(self.dict) == 1)
        self.assertEqual(id(self.dict["key"]), id(self.dict["alias"]))
        self.assertEqual(id(self.dict.get("key")), id(self.dict.get("alias")))

    def test_entryUpdatedByKeyOrAlias(
        self,
    ) -> None:
        """Test entry updates"""
        self.dict["key"] = "variant1"
        self.assertTrue(len(self.dict) == 1)
        self.assertEqual(id(self.dict["key"]), id(self.dict["alias"]))

        self.dict["alias"] = "variant2"
        self.assertTrue(len(self.dict) == 1)
        self.assertEqual(id(self.dict["key"]), id(self.dict["alias"]))

        self.dict.update(key="variant3")
        self.assertTrue(len(self.dict) == 1)
        self.assertEqual(id(self.dict["key"]), id(self.dict["alias"]))

    def test_entryDeletedByKeyOrAlias(
        self,
    ) -> None:
        """Test entry deletion."""

        def _test(
            pop_func: callable,
        ) -> None:
            """Test entry removal."""
            self.setUp()
            self.assertTrue(len(self.dict) == 1)
            pop_func()
            self.assertTrue(len(self.dict) == 0)
            self.assertTrue(self.dict.get("key") is None)
            self.assertTrue(self.dict.get("alias") is None)
            self.assertTrue(self.dict.get_alias("key") == [])

        _test(pop_func=lambda: self.dict.pop("key"))
        _test(pop_func=lambda: self.dict.pop("alias"))
        _test(pop_func=lambda: self.dict.popitem())


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
