#!/usr/bin/python
# -*- coding: ascii -*-
"""
Common SDK definitions.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import pathlib as pl
import typing as tp


# -->> Tunables <<---------------------


# -->> Definitions <<------------------
#: TyPe definition. Any value.
TPAny       = tp.TypeVar("TPAny")

#: TyPe definition. Path sources.
TPByte      = tp.TypeVar("TPByte", bytes, bytearray)

#: TyPe definition. Path sources.
TPText      = tp.TypeVar("TPText", bytes, bytearray, str)

#: TyPe definition. Path sources.
TPPath      = tp.TypeVar("TPPath", bytes, bytearray, str, pl.Path)

#: CallBack definition. Any -> Any
CBAny2Any   = tp.Callable[..., TPAny]

#: CallBack definition. Any -> None
CBAny2None  = tp.Callable[..., None]

#: CallBack definition. None -> None
CBNone2None = tp.Callable[[], None]


# -->> API <<--------------------------

