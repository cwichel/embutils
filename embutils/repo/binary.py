#!/usr/bin/python
# -*- coding: ascii -*-
"""
Binary generation utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import intelhex

from pathlib import Path
from typing import List, Tuple


# -->> Definitions <<------------------


# -->> API <<--------------------------
def bin_to_hex(file: Path, offset: int) -> intelhex.IntelHex:
    """
    Convert a binary file into an HEX.

    :param Path file: Path to source BIN file.
    :param int  offset: BIN file address offset.
    """
    out = intelhex.IntelHex()
    with file.open(mode='r') as fhex:
        out.loadbin(fobj=fhex, offset=offset)
    return out


def merge_bin(out: Path, sources: List[Tuple[Path, int]]) -> None:
    """
    Merge a group of binary files into an HEX.

    :param Path out: Path to output HEX file.
    :param list sources: List of tuples that contain:

        - BIN file path.
        - BIN file address offset
    """
    # Merge all BIN files
    tmp = intelhex.IntelHex()
    for file, addr in sources:
        cur = bin_to_hex(file=file, offset=addr)
        tmp.merge(other=cur, overlap='replace')

    # Save output
    with out.open(mode='w') as file:
        tmp.write_hex_file(file)


def merge_hex(out: Path, sources: List[Path]) -> None:
    """
    Merge a group of HEX files.

    :param Path out: Path to output HEX file.
    :param list sources: List of paths to HEX files.
    """
    # Merge all HEX files
    tmp = intelhex.IntelHex()
    for file in sources:
        cur = intelhex.IntelHex(source=f'{file}')
        tmp.merge(other=cur, overlap='replace')

    # Save output
    with out.open(mode='w') as file:
        tmp.write_hex_file(file)
