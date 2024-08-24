#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Extras libraries and utilities.

This component package contains libraries and utilities that are generic enough
to be used in multiple components/applications but are situational enough to not
be included in the core libraries.

:date:      2024
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# --------------------------------------
__author__ = "Christian Wiche"
__version__ = "ALPHA"
# --------------------------------------

# App
from .cobs import *


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------


# -->> Export <<------------------------
__all__ = [
    # cobs.py
    "COBS",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
