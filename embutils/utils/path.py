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

from .common import TPAny, TPPath


# -->> Definitions <<------------------


# -->> API <<--------------------------
def as_path(path: TPAny) -> pl.Path:
    """
    Try to convert the input to a path.

    :param tp.Any path:     Value to be converted to path.

    :return: Path
    :rtype: pl.Path

    :raises ValueError: Input can't be converted to Path.
    """
    # Avoid not compatible types
    if not isinstance(path, TPPath.__constraints__):
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


def path_validator(path: tp.Any, allow_none: bool = True,
                   check_existence: bool = False,
                   check_reachable: bool = False) -> tp.Optional[pl.Path]:
    """
    Validate if the given parameter is a path.

    :param tp.Any path:             Path to be validated.
    :param bool allow_none:         Allow None inputs.
    :param bool check_existence:    Check if the path exists.
    :param bool check_reachable:    Check if the path is reachable.

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
        raise ValueError(f"'{path}' is not reachable.")
    if check_existence and not path.exists():
        raise ValueError(f"'{path}' doesnt exist.")
    return path


def dir_validator(path: tp.Any, required: bool = False, create: bool = False):
    """
    Validate the directory path.

    :param tp.Any path:     Directory path to be validated.
    :param bool required:   Directory must exist.
    :param bool create:     Directory can be created if reachable but not found. .

    :return: Path
    :rtype: pl.Path

    :raises ValueError: Input invalid, directory not reachable or don't exist, path is not a directory.
    """
    path = path_validator(path=path, allow_none=False, check_reachable=True)
    if create:
        path.mkdir(exist_ok=True)
    if path.exists() and not path.is_dir():
        raise ValueError(f"'{path}' is not a directory.")
    if required and not path.exists():
        raise ValueError(f"'{path}' doesnt exist.")
    return path


def file_validator(path: tp.Any, required: bool = False):
    """
    Validate the file path.

    :param tp.Any path:     File path to be validated.
    :param bool required:   File must exist.

    :return: Path
    :rtype: pl.Path

    :raises ValueError: Input invalid, file not reachable or don't exist, path is not a file.
    """
    path = path_validator(path=path, allow_none=False, check_reachable=True, check_existence=required)
    if path.exists() and not path.is_file():
        raise ValueError(f"Path '{path}' is not a file.")
    return path
