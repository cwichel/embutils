#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Interface usage test.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import pytest
import unittest

from examples.stream_setup import SimplePacket, COBSStreamFramingCodec

from embutils.serial import Interface, Stream, Device
from embutils.utils import SDK_LOG


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class TestInterface(unittest.TestCase):
    """
    Basic interface tests using the SimplePacket example.
    """
    def test_01_fail(self):
        """
        Test failure cases.
        """
        # Prepare interface
        sd = Device(looped=True)
        ss = Stream(device=sd, codec=COBSStreamFramingCodec(dtype=SimplePacket))
        si = Interface(stream=ss)

        # Test timing configuration
        with pytest.raises(ValueError):
            si.timeout = -5
        with pytest.raises(ValueError):
            si.timeout = 0

        # Stop interface
        si.stop()

    def test_02_configuration(self):
        """
        Test interface configuration.
        """
        # Prepare interface
        sd = Device(looped=True)
        ss = Stream(device=sd, codec=COBSStreamFramingCodec(dtype=SimplePacket))
        si = Interface(stream=ss)

        # Test stream property
        assert si.stream == ss

        # Test timing configuration
        si.timeout = 10
        assert si.timeout == 10

        # Stop interface
        si.stop()

    def test_03_transmit(self):
        """
        Test transmission process.
        Send and receive an item using the stream on a looped serial device.
        """
        # Prepare data to send/receive
        item = SimplePacket(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))

        # Prepare interface
        sd = Device(looped=True)
        ss = Stream(device=sd, codec=COBSStreamFramingCodec(dtype=SimplePacket))
        si = Interface(stream=ss)

        # Transmission reception logic (pass-through)
        def rx_logic(rx: SimplePacket) -> bool:
            _ = rx
            return True

        # Execute tests on connect...
        def on_connected():
            # Send and receive
            recv = si.transmit(send=item, logic=rx_logic)
            assert (item is not None) and (recv is not None)
            assert item == recv

            # Send without response
            recv = si.transmit(send=item)
            assert recv is None

            si.stop()

        # Run
        si.on_connect += on_connected
        si.join()


# -->> Execute <<----------------------
if __name__ == '__main__':
    SDK_LOG.enable()
    unittest.main()
