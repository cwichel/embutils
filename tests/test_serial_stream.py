#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Serialized objects stream test.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import time
import unittest

from examples.stream_setup import SimplePacket, COBSStreamFramingCodec

from embutils.serial import Device, Stream
from embutils.utils import SDK_LOG, Timer


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class TestStream(unittest.TestCase):
    """
    Basic stream tests using the SimplePacket example.
    """
    def test_01_configuration(self):
        """
        Test stream configuration.
        """
        # Prepare interface
        sd = Device(looped=True)
        ss = Stream(device=sd, codec=COBSStreamFramingCodec(dtype=SimplePacket))

        # Test device property
        assert ss.device == sd

        # Test device configuration
        sd_new = Device(looped=True)
        ss.device = sd_new
        assert ss.device == sd_new

        # Stop interface
        ss.stop()

    def test_02_transmit(self):
        """
        Send and receive an item using the Stream on a looped serial Device.
        Test if the transmitted/received items are the same.
        """
        # Prepare data to send/receive
        data = SimplePacket(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))

        # Prepare interface
        is_ready = False
        sd = Device(looped=True)
        ss = Stream(device=sd, codec=COBSStreamFramingCodec(dtype=SimplePacket))

        # Transmission reception logic
        def on_received(item: SimplePacket):
            nonlocal is_ready
            assert (item is not None) and (data is not None)
            assert item == data
            is_ready = True

        # Execute tests on connect...
        def on_connected():
            ss.send(item=data)

        # Run
        ss.on_connect += on_connected
        ss.on_receive += on_received
        tim = Timer()
        while not is_ready:
            if tim.elapsed() > 1.0:
                assert False
            time.sleep(0.1)


# -->> Execute <<----------------------
if __name__ == '__main__':
    SDK_LOG.enable()
    unittest.main()
