#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Scripting utilities test suite.

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
from embutils.core import ScriptCallable, ScriptEntryPoint


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class ScriptTestSuite(ut.TestCase):
    def test_scriptSetup(
        self,
    ) -> None:
        """Test script callable."""

        class TestScriptCallable(ScriptCallable):
            """Test script callable."""

            def __call__(
                self,
                entry: ScriptEntryPoint,
            ) -> None:
                """Script logic."""
                self.entry = entry

        script_callable = TestScriptCallable()
        entry_point = ScriptEntryPoint(
            title="Test script",
            script=script_callable,
        )
        entry_point.main()
        self.assertEqual(
            entry_point,
            script_callable.entry,
        )


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
