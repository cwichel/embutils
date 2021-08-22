#!/usr/bin/python
# -*- coding: ascii -*-
"""
Binary utilities testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
import intelhex
import unittest
from embutils.repo import bin_to_hex, merge_bin, merge_hex
from pathlib import Path


# Test Definitions ==============================
class TestVersion(unittest.TestCase):
    """
    Test binary utilities.
    """
    OFFSET = 0x20
    FILES  = [
        (Path('base1.bin'), 'This is a test'),
        (Path('base2.bin'), 'This is yet another test')
        ]

    def __init__(self, *args, **kwargs):
        super(TestVersion, self).__init__(*args, **kwargs)
        self.generate()

    def __del__(self):
        self.clean()

    def test_01_bin2hex(self):
        """
        Test bin2hex utility.
        """
        for file, content in self.FILES:
            fhex = bin_to_hex(file=file, offset=0x20)
            assert fhex.gets(addr=0x20, length=len(content)).decode() == content

    def test_02_multi_bin2hex(self):
        """
        Test multi bin2hex utility.
        """
        # Prepare sources list
        last = 0
        sources = []
        for file, content in self.FILES:
            sources.append((file, (self.OFFSET + last)))
            last += len(content)

        # Generate hex and check
        fhex = Path('test1.hex')
        merge_bin(out=fhex, sources=sources)
        self.check_merged(file=fhex)

    def test_03_multi_hex2hex(self):
        """
        Test multi hex2hex utility.
        """
        # Prepare source files
        last = 0
        sources = []
        for file, content in self.FILES:
            fhex = file.parent / f'{file.name}.hex'
            bin_to_hex(file=file, offset=(self.OFFSET + last)).write_hex_file(fhex)
            sources.append(fhex)
            last += len(content)

        # Generate hex
        f3 = Path('test3.hex')
        merge_hex(out=f3, sources=sources)
        self.check_merged(file=f3)

    def check_merged(self, file: Path) -> None:
        """
        Check the messages on the generated HEX.
        """
        last = 0
        fhex = intelhex.IntelHex(source=f'{file}')
        for file, content in self.FILES:
            assert fhex.gets(addr=(self.OFFSET + last), length=len(content)).decode() == content
            last += len(content)

    def generate(self) -> None:
        """
        Generate the test files.
        """
        for file, content in self.FILES:
            with file.open(mode='wb') as f:
                f.write(content.encode())

    def clean(self) -> None:
        """
        Clean all the used files.
        """
        path  = Path()
        files = list(path.glob(pattern='*.hex')) + list(path.glob(pattern='*.bin'))
        for file in files:
            file.unlink(missing_ok=True)


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
