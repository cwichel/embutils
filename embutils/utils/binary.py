#!/usr/bin/python
# -*- coding: ascii -*-
"""
Binary generation utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import typing as tp

import intelhex

from .path import TPPath, path_validator


# -->> Definitions <<------------------
RECORD_BYTES = 32


# -->> API <<--------------------------
def bin_to_hex(src: TPPath, out: TPPath = None, off: int = 0x08000000) -> intelhex.IntelHex:
    """
    Convert a binary file into an HEX.

    :param TPPath src: Path to source BIN file.
    :param TPPath out: Optional. If provided, saves the generated hex file in the given path.
    :param int off:    BIN file address offset.

    :return: HEX file
    :rtype: intelhex.IntelHex
    """
    # Check paths
    src = path_validator(path=src, allow_none=False, check_reachable=True)
    out = path_validator(path=out, allow_none=True, check_reachable=True)
    # Generate HEX
    tmp = intelhex.IntelHex()
    tmp.loadbin(fobj=f"{src}", offset=off)
    # Save if required
    if out is not None:
        tmp.write_hex_file(f=f"{out}", byte_count=RECORD_BYTES)
    return tmp


def merge_bin(src: tp.List[tp.Tuple[TPPath, int]], out: TPPath = None) -> intelhex.IntelHex:
    """
    Merge a group of binary files into an HEX.

    :param list src:    List of tuples that contain:
        - BIN file path.
        - BIN file address offset
    :param TPPath out:  Optional. If provided, saves the generated hex file in the given path.

    :return: Merged HEX file.
    :rtype: intelhex.IntelHex
    """
    # Check paths
    src = [[path_validator(path=addr, allow_none=False, check_reachable=True), idx] for addr, idx in src]
    out = path_validator(path=out, allow_none=True, check_reachable=True)
    # Merge all BIN files
    tmp = intelhex.IntelHex()
    for file, addr in src:
        this = bin_to_hex(src=file, off=addr)
        tmp.merge(other=this, overlap="replace")
    # Save if required
    if out is not None:
        tmp.write_hex_file(f=f"{out}", byte_count=RECORD_BYTES)
    return tmp


def merge_hex(src: tp.List[TPPath], out: TPPath = None) -> intelhex.IntelHex:
    """
    Merge a group of HEX files.

    :param list src:    List of paths to HEX files.
    :param TPPath out:  Optional. If provided, saves the generated hex file in the given path.

    :return: Merged HEX file.
    :rtype: intelhex.IntelHex
    """
    # Check paths
    src = [path_validator(path=item, allow_none=False, check_reachable=True) for item in src]
    out = path_validator(path=out, allow_none=True, check_reachable=True)
    # Merge all HEX files
    tmp = intelhex.IntelHex()
    for file in src:
        this = intelhex.IntelHex(source=f"{file}")
        tmp.merge(other=this, overlap="replace")
    # Save if required
    if out is not None:
        tmp.write_hex_file(f=f"{out}", byte_count=RECORD_BYTES)
    return tmp
