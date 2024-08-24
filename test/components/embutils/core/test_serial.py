#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Serial utilities test suite.

:date:      2024
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# --------------------------------------
__author__ = "Christian Wiche"
__version__ = "ALPHA"
# --------------------------------------

# Built-in
import unittest as ut

# External
import serial as ser
from embutils.core import SerialDevice


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class SerialDeviceTestSuite(ut.TestCase):
    def test_setDevice(
        self,
    ) -> None:
        """Test device creation and updates."""
        # Create from URL
        dev1 = SerialDevice.from_url(url="loop://")
        self.assertIsInstance(dev1, SerialDevice)
        self.assertIsInstance(dev1.io, ser.SerialBase)
        self.assertTrue(dev1.io.is_open)
        # Create empty
        dev2 = SerialDevice()
        self.assertIsInstance(dev2, SerialDevice)
        self.assertIsNone(dev2.io)
        # Assign device
        dev2.io = dev1.io
        self.assertIsNotNone(dev2.io)
        self.assertIsInstance(dev2.io, ser.SerialBase)
        # Device is closed on replacement
        dev1.io = None
        self.assertIsNone(dev1.io)
        self.assertFalse(dev2.io.is_open)

    def test_deviceInfo(
        self,
    ) -> None:
        """Test device info."""
        dev = SerialDevice.from_url(url="loop://")
        # For loop the info is not available
        self.assertIsNone(dev.info)

    def test_dataTransfer(
        self,
    ) -> None:
        """Test data transfer."""
        dev = SerialDevice.from_url(url="loop://")
        # Test transfer
        dev.io.write(b"test")
        self.assertEqual(dev.io.read(4), b"test")


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
