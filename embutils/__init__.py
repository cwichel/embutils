#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Embutils main module.

This is the entry point for the Embutils module.

:date:      2022
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------
__version__ = "2022.10.18"
# --------------------------------------


# -->> Tunables <<---------------------


# -->> Definitions <<------------------
def some_function(arg1, arg2):
    return arg1 + arg2


# -->> API <<--------------------------
def version() -> str:
    """Embutils version string.

    :return: version
    :rtype: str
    """
    return __version__
