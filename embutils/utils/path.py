#!/usr/bin/python
# -*- coding: ascii -*-
"""
Path checking utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import pathlib as pl
import typing as tp


# -->> Definitions <<------------------
#: TyPe definition. Path sources.
TPPath = tp.Union[bytes, bytearray, str, pl.Path]


# -->> API <<--------------------------
def as_path(path: tp.Any) -> pl.Path:
    """
    Try to convert the input to a path.

    :param tp.Any path:     Value to be converted to path.

    :return: Path
    :rtype: pl.Path

    :raises ValueError: Input can't be converted to Path.
    """
    # Avoid not compatible types
    if not isinstance(path, tp.get_args(TPPath)):
        raise ValueError(f"Parameter with value '{path}' can't be converted to path.")
    # Convert
    try:
        return pl.Path(path)
    except TypeError:
        return pl.Path(path.decode(errors="ignore"))


def path_reachable(path: pl.Path) -> bool:
    """
    Check if a path is reachable.

    :param pl.Path path:    Path to be reached.

    :return: True if the path or its parent exist.
    :rtype: bool
    """
    return path.exists() or path.parent.exists()


def path_validator(path: tp.Any, allow_none: bool = True, check_reachable: bool = False) -> tp.Optional[pl.Path]:
    """
    Validate if the given parameter is a path.

    :param tp.Any path:             Path to be validated.
    :param bool allow_none:         Allow None inputs.
    :param bool check_reachable:    Checks if the path is reachable.

    :return: Path
    :rtype: pl.Path

    :raises ValueError: Input can't be converted to path or is not reachable.
    """
    # Check if input is none
    if path is None:
        if allow_none:
            return None
        raise ValueError("Parameter 'None' is not accepted as path.")
    # Validate
    path = as_path(path=path)
    if check_reachable and not path_reachable(path=path):
        raise ValueError(f"Path '{path}' is not reachable.")
    return path
