#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Scripting utilities.

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
import dataclasses as dc
import typing as tp


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
@tp.runtime_checkable
class ScriptCallable(tp.Protocol):
    """Script callable protocol."""

    def __call__(
        self,
        entry: "ScriptEntryPoint",
    ) -> None:
        """Script logic.

        :param entry: Script entry point.
        """


@dc.dataclass
class ScriptEntryPoint:
    """Script entry point.

    :param title: Script title.
    :param script: Script callable.
    """

    title: str = dc.field()
    script: ScriptCallable = dc.field()

    def main(
        self,
    ) -> None:
        """Script entry point. Runs the script."""
        self.prepare()
        print(self.title)
        self.script(entry=self)

    def prepare(
        self,
    ) -> None:
        """Script preparation. Use for argument parsing and validation."""


# -->> API <<---------------------------


# -->> Export <<------------------------
__all__ = [
    "ScriptCallable",
    "ScriptEntryPoint",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
