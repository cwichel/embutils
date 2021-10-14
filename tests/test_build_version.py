#!/usr/bin/python
# -*- coding: ascii -*-
"""
Version definition testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import pytest
import unittest

from pathlib import Path

from embutils.repo import VersionGit, export_version_c


# -->> Definitions <<------------------


# -->> Test API <<---------------------
class TestVersion(unittest.TestCase):
    """
    Test version utilities.
    """
    def test_01_fail(self):
        """
        Test failure cases.
        """
        ver  = VersionGit()
        file = Path('this/is/not/reachable.txt')

        # Unable to reach path to save version file
        with pytest.raises(ValueError):
            ver.save(file=file)

        # Unable to find version file to load
        with pytest.raises(ValueError):
            ver.load(file=file)

        # Unable to find path to generate version header
        with pytest.raises(ValueError):
            export_version_c(ver=ver, author="Test", note="None", file=file.parent)

    def test_02_git_build(self):
        """
        Test Git build value retrieve operations.
        """
        ver = VersionGit()
        path = Path("C:")

        # Check initial build value
        assert ver.build == ver.UVER_BUILD

        # Get build from non-git directory
        ver.update_build(path=path)
        assert ver.build == ver.UVER_BUILD

        # Get build from this repo...
        ver.update_build()
        assert ver.build != ver.UVER_BUILD

    def test_03_git_storage(self):
        """
        Test version file load/save and C headers generation.
        """
        ver_file = Path('version.txt')
        ver_head = Path('version.h')

        # Generate and store version
        ver_base = VersionGit()
        ver_base.update_build()
        ver_base.save(file=ver_file, store_build=True)

        # Load and check version
        ver_load = VersionGit.load(file=ver_file)
        assert ver_base == ver_load

        # Export version header
        export_version_c(ver=ver_load, author='test', note='version header file', file=ver_head)
        with ver_head.open('r') as f:
            data = f.read()
            assert ('test' in data) and ('version header file' in data)
            assert f'"{ver_load.major}.{ver_load.minor}.{ver_load.build}"' in data

        # Clean
        ver_file.unlink()
        ver_head.unlink()


# -->> Test Execution <<---------------
if __name__ == '__main__':
    unittest.main()
