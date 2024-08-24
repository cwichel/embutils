#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Schema libraries and utilities.

This component package contains libraries and utilities that are used by other
components to implement schemas and schema-related functionality.

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
from .entity import *
from .model import *


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------


# -->> Export <<------------------------
__all__ = [
    # entity.py
    "Component",
    "Entity",
    # model.py
    "BaseModel",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
