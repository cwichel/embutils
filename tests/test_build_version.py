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
from embutils.repo import VersionGit
from pathlib import Path


# Test Definitions ==============================
class TestVersion(unittest.TestCase):
    """
    Test version utilities.
    """
    def test_01_bump(self):
        """
        Test version bump.
        """
        v = VersionGit()

        # Test major bump
        base = v.major
        v.bump_version(ver='major')
        assert v.major == (base + 1)

        # Test minor bump
        base = v.minor
        v.bump_version(ver='minor')
        assert v.minor == (base + 1)

        # Test version set
        v.bump_version(ver='123.456')
        assert (v.major == 123) and (v.minor == 456)

        # Test fail
        try:
            v.bump_version(ver='anything')
            assert False
        except ValueError:
            assert True

    def test_02_storage(self):
        """
        Test version file save/load
        """
        f = Path()
        v = f / 'version.txt'

        # Get version
        v_base = VersionGit()
        v_base.get_build()

        # Save and load
        v_base.save_version(path=f, store_build=True)
        v_load = VersionGit().load_version(path=f)
        assert v_base == v_load

        # Clean
        v.unlink()


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
