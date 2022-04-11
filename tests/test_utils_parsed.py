#!/usr/bin/python
# -*- coding: ascii -*-
"""
Parsed usage test.

:date:      2022
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import typing as tp
import shutil

import pytest
import unittest

import attr

from embutils.utils import Path, ParseModel, ParseProtocol, TPByte, TPPath, TPText


# -->> Tunables <<---------------------


# -->> Definitions <<------------------
@attr.define
class ItemConv(ParseModel):
    b:      TPByte  = attr.field(factory=bytearray)
    p:      TPPath  = attr.field(default=None)
    t:      TPText  = attr.field(default=None)


@attr.define
class Item(ParseModel):
    s:      str     = attr.field()


@attr.define
class Container(ParseModel):
    items:  tp.List[Item] = attr.field()


# -->> API <<--------------------------
class TestParse(unittest.TestCase):
    """
    Test parser utility.
    """
    TEST_PATH    = Path("tmp")

    def __init__(self, *args, **kwargs):
        """
        Generate base files used on the test.
        """
        super(TestParse, self).__init__(*args, **kwargs)
        self._create()

    def __del__(self):
        """
        Remove test files after execution.
        """
        self._clean()

    def test_01_errors(self) -> None:
        """
        Test parsing errors.
        """
        # Non-compatible objects to parse...
        with pytest.raises(ValueError):
            Item.parse_obj(obj=1)
        with pytest.raises(ValueError):
            Item.parse_obj(obj=3.25)
        with pytest.raises(ValueError):
            Item.parse_obj(obj='{"s": "this is"}')

        # Unable to get protocol from filename...
        with pytest.raises(ValueError):
            Item.parse_file(path=self.TEST_PATH / "test.txt")

    def test_02_structures(self) -> None:
        """
        Test single structure conversion.
        """
        tests = [
            (
                Item,
                Item("test"),
                {"s": "test"}
            ),
            (
                Container,
                Container([Item("test1"), Item("test2")]),
                {"items": [{"s": "test1"}, {"s": "test2"}]}
            ),
        ]
        for dtype, struct, unstruct in tests:
            assert struct.dict() == unstruct
            assert dtype.parse_obj(obj=unstruct) == struct

    def test_03_conversions(self) -> None:
        """
        Test list of single structures.
        """
        tests = [
            (
                ItemConv,
                ItemConv(b=bytearray([1, 2, 3])),
                {"b": "AQID\n"}
            ),
            (
                ItemConv,
                ItemConv(p=Path("text.txt")),
                {"p": "text.txt"}
            ),
            (
                ItemConv,
                ItemConv(t="This is a text"),
                {"t": "This is a text"}
            ),
        ]
        for dtype, struct, unstruct in tests:
            assert struct.dict() == unstruct
            assert dtype.parse_obj(obj=unstruct) == struct

    def test_04_files(self) -> None:
        """
        Test file export/import.
        """
        tests = [
            (
                Container,
                ParseProtocol.YAML,
                Container(items=[Item(s="this is"), Item(s="a test!")]),
                "items:\n- s: this is\n- s: a test!\n"
            ),
            (
                Container,
                ParseProtocol.JSON,
                Container(items=[Item(s="this is"), Item(s="a test!")]),
                '{"items": [{"s": "this is"}, {"s": "a test!"}]}'
            ),
        ]
        for dtype, protocol, struct, encoded in tests:
            path = self.TEST_PATH / f"test{protocol.value.suffixes[0]}"
            assert struct.export(path=path, protocol=protocol) == encoded
            assert dtype.parse_file(path=path) == struct

    def _create(self):
        """
        Create the test assets.
        """
        self.TEST_PATH.mkdir(exist_ok=True)

    def _clean(self):
        """
        Clean all test assets.
        """
        if self.TEST_PATH.exists():
            shutil.rmtree(path=self.TEST_PATH)


# -->> Execute <<----------------------
if __name__ == '__main__':
    unittest.main()
