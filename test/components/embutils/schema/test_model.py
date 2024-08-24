#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Base schema model implementation test suite.

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
import pydantic as pdt
from embutils.schema import BaseModel


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class BaseModelTestSuite(ut.TestCase):
    def test_fromObject(
        self,
    ) -> None:
        """Test instance creation from object."""

        class TestItem(BaseModel):
            a: int = pdt.Field()
            b: str = pdt.Field(default="test")

        # Validate initialization from list, tuples, and dicts
        tests = [
            {},
            {"a": 1},
            {"a": 1, "b": "sample"},
            {"a": 1, "b": "sample", "c": "ignored"},
        ]
        for test in tests:
            scenarios = [
                test,
                list(test.values()),
                tuple(test.values()),
            ]
            for scenario in scenarios:
                if len(scenario) == 0:
                    self.assertRaises(pdt.ValidationError, TestItem.parse, scenario)
                else:
                    model = TestItem.parse(scenario)
                    self.assertEqual(model.a, 1)
                    if len(scenario) > 1:
                        self.assertEqual(model.b, "sample")
                    else:
                        self.assertEqual(model.b, "test")
        # Validate initialization with other object
        src = TestItem(a=1, b="sample")
        dst = TestItem.parse(src)
        self.assertEqual(src, dst)
        self.assertNotEqual(id(src), id(dst))


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
