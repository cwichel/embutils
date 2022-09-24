#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
<TBD>

:date:      2022
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------


# Built-in
import unittest as ut

# External
from parametrize import parametrize

# Project
import embutils as embu


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class ExampleTestCases(ut.TestCase):
    @parametrize(("a", "b", "expected"), [(1, 2, 3), (2, 4, 6), (-2, -3, -5), (-5, 5, 0)])
    def test_some_function(self, a, b, expected):
        self.assertEqual(embu.some_function(a, b), expected)


# -->> Execute <<----------------------
if __name__ == "__main__":
    ut.main()
