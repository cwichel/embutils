#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Common SDK definitions.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import pathlib as pl
import typing as tp


# -->> Tunables <<---------------------


# -->> Definitions <<------------------
#: Default message encoding
ENCODE      = "utf-8"

#: TyPe definition. Any value.
TPAny       = tp.Any

#: TyPe definition. Path sources.
TPByte      = tp.Union[bytes, bytearray]

#: TyPe definition. Path sources.
TPText      = tp.Union[TPByte, str]

#: TyPe definition. Path sources.
TPPath      = tp.Union[TPText, pl.Path]

#: CallBack definition. Any -> Any
CBAny2Any   = tp.Callable[..., TPAny]

#: CallBack definition. Any -> None
CBAny2None  = tp.Callable[..., None]

#: CallBack definition. None -> None
CBNone2None = tp.Callable[[], None]


# -->> API <<--------------------------


# -->> Export <<-----------------------
__all__ = [
    "ENCODE",
    "TPAny",
    "TPByte",
    "TPText",
    "TPPath",
    "CBAny2Any",
    "CBAny2None",
    "CBNone2None",
    ]
