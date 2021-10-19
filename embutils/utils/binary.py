#!/usr/bin/python
# -*- coding: ascii -*-
"""
Binary generation utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import pathlib as pl
import typing as tp

import intelhex


# -->> Definitions <<------------------
RECORD_BYTES = 32


# -->> API <<--------------------------
def bin_to_hex(src: pl.Path, off: int, out: tp.Optional[pl.Path] = None) -> intelhex.IntelHex:
    """
    Convert a binary file into an HEX.

    :param pl.Path src: Path to source BIN file.
    :param int off:     BIN file address offset.
    :param pl.Path out: Optional. If set, saves the generated hex file in the given path.

    :return: HEX file
    :rtype: intelhex.IntelHex
    """
    # Generate HEX
    tmp = intelhex.IntelHex()
    tmp.loadbin(fobj=f'{src}', offset=off)

    # Save if required
    if isinstance(out, pl.Path):
        tmp.write_hex_file(f=f'{out}', byte_count=RECORD_BYTES)
    return tmp


def merge_bin(src: tp.List[tp.Tuple[pl.Path, int]], out: tp.Optional[pl.Path] = None) -> intelhex.IntelHex:
    """
    Merge a group of binary files into an HEX.

    :param list src:    List of tuples that contain:
        - BIN file path.
        - BIN file address offset
    :param pl.Path out: Optional. If set, saves the generated hex file in the given path.

    :return: Merged HEX file.
    :rtype: intelhex.IntelHex
    """
    # Merge all BIN files
    tmp = intelhex.IntelHex()
    for file, addr in src:
        this = bin_to_hex(src=file, off=addr)
        tmp.merge(other=this, overlap='replace')

    # Save if required
    if isinstance(out, pl.Path):
        tmp.write_hex_file(f=f'{out}', byte_count=RECORD_BYTES)
    return tmp


def merge_hex(src: tp.List[pl.Path], out: tp.Optional[pl.Path] = None) -> intelhex.IntelHex:
    """
    Merge a group of HEX files.

    :param list src:    List of paths to HEX files.
    :param pl.Path out: Optional. If set, saves the generated hex file in the given path.

    :return: Merged HEX file.
    :rtype: intelhex.IntelHex
    """
    # Merge all HEX files
    tmp = intelhex.IntelHex()
    for file in src:
        this = intelhex.IntelHex(source=f'{file}')
        tmp.merge(other=this, overlap='replace')

    # Save if required
    if isinstance(out, pl.Path):
        tmp.write_hex_file(f=f'{out}', byte_count=RECORD_BYTES)
    return tmp
