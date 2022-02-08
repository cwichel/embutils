#!/usr/bin/python
# -*- coding: ascii -*-
"""
Path utility testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import shutil

import pytest
import unittest

from embutils.utils import Path, FileTypeError, FileSuffixError


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class TestPath(unittest.TestCase):
    """
    Test path utility.
    """
    TEST_PATH = Path("tmp")
    TEST_FILE = TEST_PATH / "test.txt"

    def __del__(self):
        """
        Ensure to clean test files.
        """
        self._clean()

    def test_01_path_error(self):
        """
        Path and common validator error tests.
        """
        # Init
        self._clean()

        # Error: Data type.
        with pytest.raises(TypeError):
            Path(1)
        with pytest.raises(TypeError):
            Path(3.256)
        # Error: None input
        with pytest.raises(ValueError):
            Path.validate(path=None, none_ok=False)
        # Error: Path not reachable
        with pytest.raises(FileNotFoundError):
            Path.validate(path=(self.TEST_PATH / "reach_issue"), reachable=True)
        # Error: Path dont exists
        with pytest.raises(FileNotFoundError):
            Path.validate(path=self.TEST_PATH, must_exist=True)

    def test_01_path(self):
        """
        Path and common validator tests.
        """
        # Supported types
        assert Path() is not None
        assert Path("test")
        assert Path(b"test")
        assert Path(bytearray(b"test"))

    def test_03_dir_error(self):
        """
        Directory path validation error tests.
        """
        # Error: Directory dont exist
        self._clean()
        with pytest.raises(FileNotFoundError):
            Path.validate_dir(path=self.TEST_PATH, must_exist=True)
        # Error: Path is a file
        self._create_test_file()
        with pytest.raises(FileTypeError):
            Path.validate_dir(path=self.TEST_FILE)

    def test_04_dir(self):
        """
        Directory path validation tests.
        """
        # Init
        self._clean()
        # Allowing None input
        assert Path.validate_dir(path=None, none_ok=True) is None
        # Path address is reachable (or exists)
        assert Path.validate_dir(path=self.TEST_PATH)
        # Path create
        assert Path.validate_dir(path=self.TEST_PATH, create=True)
        # Path exist
        assert Path.validate_dir(path=self.TEST_PATH, must_exist=True)

    def test_05_file_error(self):
        """
        File path validation error tests.
        """
        # Error: File dont exist
        self._clean()
        self._create_test_dir()
        with pytest.raises(FileNotFoundError):
            Path.validate_file(path=self.TEST_FILE, must_exist=True)
        # Error: Path is a directory
        with pytest.raises(FileTypeError):
            Path.validate_file(path=self.TEST_PATH)
        # Error: File suffixes
        self._create_test_file()
        with pytest.raises(FileSuffixError):
            Path.validate_file(path=self.TEST_FILE, must_exist=True, suffixes=[".yaml", ".json"])

    def test_06_file(self):
        """
        File path validation tests.
        """
        # Init
        self._clean()
        self._create_test_dir()

        # Allowing None input
        assert Path.validate_file(path=None, none_ok=True) is None

        # Path address is reachable (or exists)
        assert Path.validate_file(path=self.TEST_FILE)

        # Path address is reachable (or exists) when testing with default file name
        assert Path.validate_file(path=self.TEST_PATH, default=self.TEST_FILE.name)

        # Path exist
        self._create_test_file()
        assert Path.validate_file(path=self.TEST_FILE, must_exist=True)

    def _create_test_dir(self) -> None:
        """
        Create the test directory.
        """
        if not self.TEST_PATH.exists():
            self.TEST_PATH.mkdir()

    def _create_test_file(self) -> None:
        """
        Create the test file.
        """
        self._create_test_dir()
        with self.TEST_FILE.open("w") as f:
            f.write('Test file')

    def _clean(self) -> None:
        """
        Clean all test assets.
        """
        if self.TEST_PATH.exists():
            shutil.rmtree(path=self.TEST_PATH)


# -->> Execute <<----------------------
if __name__ == '__main__':
    unittest.main()
