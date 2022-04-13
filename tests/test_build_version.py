#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Version repository definition testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import copy as cp
import shutil

import pytest
import unittest

from embutils.repo import (VersionHandler, GitBuildVersionUpdater, CCppVersionExporter, SimpleVersionStorage)
from embutils.utils import Path, FileTypeError


# -->> Tunables <<---------------------


# -->> Definitions <<------------------
#: Uninitialized version definition
ver_error = VersionHandler()
#: Initialized version definition
ver_init = VersionHandler(updater=GitBuildVersionUpdater(), storage=SimpleVersionStorage(), exporter=CCppVersionExporter())


# -->> API <<--------------------------
class TestVersion(unittest.TestCase):
    """
    Test version utilities.
    """
    TEST_PATH = Path("tmp")

    def __init__(self, *args, **kwargs):
        """
        Generate base files used on the test.
        """
        super(TestVersion, self).__init__(*args, **kwargs)
        self._create()

    def __del__(self):
        """
        Remove test files after execution.
        """
        self._clean()

    def test_01_fail(self):
        """
        Common test failure cases.
        """
        path = Path("this/is/not/reachable.txt")

        # Uninitialized handlers
        for func in [ver_error.load, ver_error.save, ver_error.export, ver_error.update]:
            with pytest.raises(RuntimeError):
                func()

        # Unable to reach path to save version file
        with pytest.raises(FileNotFoundError):
            ver_init.save(path=path)

        # Unable to find version file to load
        with pytest.raises(FileNotFoundError):
            ver_init.load(path=path)

        # Unable to find path to generate version header
        with pytest.raises(FileNotFoundError):
            ver_init.export(author="Test", path=path.parent)

    def test_02_storage_simple(self):
        """
        Test simple version storage operations.
        """
        path = self.TEST_PATH / "version.txt"

        # Version storage
        ver_init.save(path=path)
        assert path.exists() and path.is_file()

        # Version load
        ver_test = cp.copy(ver_init)
        ver_test.load(path=path)

        # Check
        assert ver_test is not ver_init
        assert ver_test == ver_init

    def test_03_update_git(self):
        """
        Test Git version update operations.
        """
        path = Path("C:/")

        # Get build from non-git directory
        ver_init.update(path=path)
        assert ver_init.build == GitBuildVersionUpdater.NO_BUILD

        # Get build from this repo...
        ver_init.update()
        assert ver_init.build != GitBuildVersionUpdater.NO_BUILD

    def test_04_exporter_ccpp(self):
        """
        Test C/C++ version exporter operations.
        """
        path    = self.TEST_PATH / "version.h"
        author  = "Test"

        # Test suffix issue
        with pytest.raises(FileTypeError):
            ver_init.export(path=Path("version.c"), author=author)

        # Export version header
        ver_init.export(path=path, author=author)

        # Check
        data = path.open(mode="r").read()
        assert path.exists() and path.is_file()
        assert path.name in data
        assert author in data
        assert str(ver_init) in data

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
