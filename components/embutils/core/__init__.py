#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Core libraries and utilities.

This component package contains the core libraries and utilities used by the
other components of the framework.

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
from .bytes import *
from .crc import *
from .dict import *
from .enum import *
from .event import *
from .execute import *
from .logger import *
from .script import *
from .serial import *


# -->> Tunables <<---------------------


# -->> Definitions <<------------------
LOGGER = create_logger()
"""Application logger."""


# -->> API <<--------------------------


# -->> Export <<------------------------
__all__ = [
    # bytes.py
    "bit",
    "bit_mask",
    "bit_reverse",
    # crc.py
    "CRC",
    # dict.py
    "DictAlias",
    # enum.py
    "EnumUtils",
    # event.py
    "EventTarget",
    "EventSlot",
    "Events",
    # execute.py
    "execute",
    # logger.py
    "LoggerSettings",
    "create_logger",
    "shutdown_logger",
    # script.py
    "ScriptCallable",
    "ScriptEntryPoint",
    # serial.py
    "SerialDevice",
    # __init__.py
    "LOGGER",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
