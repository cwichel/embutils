#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Subprocess execution utilities test suite.

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
import contextlib as ctx
import io
import pathlib as pl
import unittest as ut

# External
from embutils.core import execute


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class ExecuteTestSuite(ut.TestCase):
    def test_captureModes(
        self,
    ) -> None:
        """Test capture modes."""
        msg = "Hello World!"
        buffer = io.StringIO()
        # Full: No stdout, only on result
        with ctx.redirect_stdout(buffer):
            result = execute(cmd=["python", "-c", f"print('{msg}')"], capture="full")
            self.assertEqual(first="", second=buffer.getvalue())
            self.assertIn(member=msg, container=result.stdout)
        # Mirror: Both stdout and result
        with ctx.redirect_stdout(buffer):
            result = execute(cmd=["python", "-c", f"print('{msg}')"], capture="mirror")
            self.assertIn(member=msg, container=buffer.getvalue())
            self.assertIn(member=msg, container=result.stdout)
        # None: Only stdout
        with ctx.redirect_stdout(buffer):
            result = execute(cmd=["python", "-c", f"print('{msg}')"], capture="none")
            self.assertIn(member=msg, container=buffer.getvalue())
            self.assertIsNone(obj=result.stdout)

    def test_executeLog(
        self,
    ) -> None:
        """Test execute log."""
        msg = "Hello World!"
        logfile = pl.Path("test.log")
        # Log to file
        result = execute(cmd=["python", "-c", f"print('{msg}')"], logfile=logfile)
        with logfile.open("r") as file:
            contents = file.read()
            self.assertIn(member=f"print('{msg}')", container=contents)
            self.assertIn(member=f"RET : {result.returncode}", container=contents)
            self.assertIn(member=f"OUT :\n{msg}", container=contents)
        # Cleanup
        if logfile.exists():
            logfile.unlink()


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
