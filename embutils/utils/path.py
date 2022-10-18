#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Path manipulation utilities.

:date:      2022
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

# Built-in
import itertools as it
import pathlib as pl
import re
import shutil as sh
import typing as tp


# -->> Tunables <<---------------------


# -->> Definitions <<------------------
_PATTERN_SPLIT_RE = r";|:|\|"
"""str: Pattern used to split search patterns."""


# -->> API <<--------------------------
class FileTypeError(OSError):
    """File type is not the expected/supported."""


class FileSuffixError(OSError):
    """File suffix is not the expected/supported."""


def validate_path(
    path: tp.Optional[tp.Union[str, pl.Path]],
    none_ok: bool = False,
    reachable: bool = False,
    must_exist: bool = False,
) -> tp.Optional[pl.Path]:
    """Validate the provided path.

    :param tp.Optional[tp.Union[str, pl.Path]] path:    Path to validate
    :param bool none_ok:                                Allows None input
    :param bool reachable:                              Path must be reachable
    :param bool must_exist:                             Path must exist

    :return: Validated path.
    :rtype: pl.Path
    """
    if path is None:
        if none_ok:
            return None
        raise ValueError("None is not a valid path!")
    path = pl.Path(path)
    if reachable and not path.parent.exists():
        raise FileNotFoundError(f'Path is not reachable: "{path}"')
    if must_exist and not path.exists():
        raise FileExistsError(f'Path doesnt exist: "{path}"')
    return path


def validate_file(
    path: tp.Optional[tp.Union[str, pl.Path]],
    none_ok: bool = False,
    must_exist: bool = False,
    suffixes: tp.List[str] = None,
) -> tp.Optional[pl.Path]:
    """Validate the provided file path.

    :param tp.Optional[tp.Union[str, pl.Path]] path:    Path to validate
    :param bool none_ok:                                Allows None input
    :param bool must_exist:                             File must exist
    :param tp.List[str] suffixes:                       List of supported file suffixes

    :return: Validated path.
    :rtype: pl.Path
    """
    path = validate_path(
        path=path,
        none_ok=(none_ok and not must_exist),
        must_exist=must_exist,
        reachable=True,
    )
    if path is None:
        return path
    if path.exists() and not path.is_file():
        raise FileTypeError(f'Path is not a file: "{path}"')
    if suffixes and (path.suffix.lower() not in [item.lower() for item in suffixes]):
        raise FileSuffixError(f'Suffix not supported for "{path}": expected {suffixes} but got {path.suffix.lower()}')
    return path


def validate_dir(
    path: tp.Optional[tp.Union[str, pl.Path]],
    none_ok: bool = False,
    must_exist: bool = False,
    create: bool = False,
) -> tp.Optional[pl.Path]:
    """Validate the provided directory path.

    :param tp.Optional[tp.Union[str, pl.Path]] path:    Path to validate
    :param bool none_ok:                                Allows None input
    :param bool must_exist:                             Directory must exist
    :param bool create:                                 Create if it doesn't exist

    :return: Validated path.
    :rtype: pl.Path
    """
    path = validate_path(
        path=path,
        none_ok=(none_ok and not must_exist),
        must_exist=(must_exist and not create),
        reachable=True,
    )
    if path is None:
        return path
    if create and not path.exists():
        path.mkdir()
    if path.exists() and not path.is_dir():
        raise FileTypeError(f"Path is not a dir: {path}")
    return path


def find_in_path(
    path: tp.Optional[tp.Union[str, pl.Path]],
    pattern: tp.Union[str, tp.List[str]],
    rglob: bool = False,
) -> tp.List[pl.Path]:
    """Search the provided path for multiple patterns.
    The patterns should be separated by ":", ";" or "|" characters.

    :param tp.Optional[tp.Union[str, pl.Path]] path:    Path to search in
    :param tp.Union[str, tp.List[str]] pattern:         Pattern(s) to search for
    :param bool rglob:                                  Enable recursive search on path

    :return: List of paths that match the provided patterns.
    :rtype: tp.List[pl.Path]
    """
    path = validate_dir(path=path, must_exist=True)
    find = path.rglob if rglob else path.glob
    items = re.split(pattern=_PATTERN_SPLIT_RE, string=pattern) if isinstance(pattern, str) else pattern
    match = list(map(lambda x: find(pattern=x.strip()), items))
    return list(it.chain(*match))


def which(
    pattern: tp.Union[str, tp.List[str]],
    required: bool = True,
) -> tp.List[pl.Path]:
    """Search the system PATH for multiple patterns.
    The patterns should be separated by ":", ";" or "|" characters.

    :param tp.Union[str, tp.List[str]] pattern: Pattern(s) to search for
    :param bool required:                       Raises an exception if no item is found

    :return: List of paths that match the provided patterns.
    :rtype: tp.List[pl.Path]
    """
    items = re.split(pattern=_PATTERN_SPLIT_RE, string=pattern) if isinstance(pattern, str) else pattern
    match = [pl.Path(item) for item in list(map(lambda x: sh.which(cmd=x.strip()), items)) if item is not None]
    if required and not match:
        raise FileNotFoundError(f"Unable to find {pattern} on PATH")
    return match


# -->> Export <<-----------------------
__all__ = [
    # Classes
    "FileSuffixError",
    "FileTypeError",
    # Methods
    "validate_path",
    "validate_file",
    "validate_dir",
    "find_in_path",
    "which",
]
"""tp.List[str]: Module available definitions"""
