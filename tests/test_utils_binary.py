#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Binary file utilities testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import shutil

import intelhex
import unittest

from embutils.utils import ENCODE, Path, bin_to_hex, merge_bin, merge_hex


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class TestBinary(unittest.TestCase):
    """
    Test binary files utilities.
    """
    OFFSET      = 0x20
    TEST_PATH   = Path("tmp")
    TEST_FILES  = [
        (TEST_PATH / "base1.bin", "This is a test"),
        (TEST_PATH / "base2.bin", "This is yet another test")
        ]

    def __init__(self, *args, **kwargs):
        """
        Generate base files used on the test.
        """
        super(TestBinary, self).__init__(*args, **kwargs)
        self._create()

    def __del__(self):
        """
        Remove test files after execution.
        """
        self._clean()

    def test_01_bin2hex(self):
        """
        Test bin > hex file conversion.
        """
        for file, content in self.TEST_FILES:
            fout = file.parent / f"{file.stem}.hex"
            fhex = bin_to_hex(src=file, off=0x20, out=fout)
            assert intelhex.IntelHex(source=f"{fout}").todict() == fhex.todict()
            assert fhex.gets(addr=0x20, length=len(content)).decode(encoding=ENCODE, errors="ignore") == content

    def test_02_multi_bin2hex(self):
        """
        Test bin > hex file conversion and merge.
        """
        last = 0
        sources = []
        for file, content in self.TEST_FILES:
            sources.append((file, (self.OFFSET + last)))
            last += len(content)

        # Generate hex and check
        fhex = self.TEST_PATH / "test.hex"
        merge_bin(out=fhex, src=sources)
        self._check_merged(file=fhex)

    def test_03_multi_hex2hex(self):
        """
        Test hex file merge.
        """
        last = 0
        sources = []
        for file, content in self.TEST_FILES:
            fhex = file.parent / f"{file.name}.hex"
            bin_to_hex(src=file, off=(self.OFFSET + last)).write_hex_file(fhex)
            sources.append(fhex)
            last += len(content)

        # Generate hex
        fhex = self.TEST_PATH / "test.hex"
        merge_hex(out=fhex, src=sources)
        self._check_merged(file=fhex)

    def _check_merged(self, file: Path):
        """
        Check merged files against sources.
        """
        last = 0
        fhex = intelhex.IntelHex(source=f"{file}")
        for file, content in self.TEST_FILES:
            assert fhex.gets(addr=(self.OFFSET + last), length=len(content)).decode(encoding=ENCODE, errors="ignore") == content
            last += len(content)

    def _create(self):
        """
        Create the test assets.
        """
        self.TEST_PATH.mkdir(exist_ok=True)
        for file, content in self.TEST_FILES:
            with file.open(mode='wb') as f:
                f.write(content.encode(encoding=ENCODE))

    def _clean(self):
        """
        Clean all test assets.
        """
        if self.TEST_PATH.exists():
            shutil.rmtree(path=self.TEST_PATH)


# -->> Execute <<----------------------
if __name__ == '__main__':
    unittest.main()
