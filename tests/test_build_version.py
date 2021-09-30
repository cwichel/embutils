#!/usr/bin/python
# -*- coding: ascii -*-
"""
Version definition testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import unittest

from pathlib import Path

from embutils.repo import VersionGit, export_version_c


# -->> Definitions <<------------------


# -->> Test API <<---------------------
class TestVersion(unittest.TestCase):
    """
    Test version utilities.
    """
    def test_01_build(self):
        """
        Test version build.
        """
        # Initial values
        v = VersionGit()
        assert v.build == v.UVER_BUILD

        # Get build
        v.update_build()
        assert v.build != v.UVER_BUILD

    def test_02_storage(self):
        """
        Test version file save/load
        """
        fver = Path('version.txt')
        hver = Path('version.h')

        # Generate and store version
        v_base = VersionGit()
        v_base.update_build()
        v_base.save(file=fver, store_build=True)

        # Load and check version
        v_load = VersionGit.load(file=fver)
        assert v_base == v_load

        # Export version header
        export_version_c(ver=v_load, author='test', note='version header file', file=hver)
        with hver.open('r') as f:
            data = f.read()
            assert ('test' in data) and ('version header file' in data)
            assert f'"{v_load.major}.{v_load.minor}.{v_load.build}"' in data

        # Clean
        fver.unlink()
        hver.unlink()


# -->> Test Execution <<---------------
if __name__ == '__main__':
    unittest.main()
