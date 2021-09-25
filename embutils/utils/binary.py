#!/usr/bin/python
# -*- coding: ascii -*-
"""
Binary generation utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from pathlib import Path
from typing import List, Tuple

import intelhex

from .math import closest_multi


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


def shrink_hex(file: Path, empty: int = 0xFF, block: int = 4, count: int = 4) -> intelhex.IntelHex:
    """
    Remove all the empty byte blocks from the input HEX file.

    By default this function considers blocks of 4 bytes with value 0xFF as empty. If more than
    4 consecutive blocks are detected then the section is cleaned.

    :param Path file:   Path to hex file to shrink.
    :param int empty:   Empty byte value.
    :param int block:   Number of empty bytes that form a clean block.
    :param int count:   Minimum number of consecutive blocks to trigger cleaning.

    :return: Reduced Hex file
    :rtype: intelhex.IntelHex
    """
    output  = intelhex.IntelHex(source=f'{file}')

    # Define reference values
    check   = empty * block
    start   = int(closest_multi(ref=output.minaddr(), base=block))
    end     = output.maxaddr()

    # Clean Process
    detected  = 0
    addr_init = 0
    addr_last = 0
    for addr_last in range(start, end, block):
        data = output.gets(addr=addr_last, length=block)
        test = (sum(data) == check)
        if test:
            if detected == 0:
                addr_init = addr_last
            detected += 1
        else:
            if detected >= count:
                del output[addr_init:addr_last]
            detected = 0

    # Handle last detection
    if detected >= count:
        del output[addr_init:(addr_last + block)]

    # Return result
    return output
