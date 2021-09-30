#!/usr/bin/python
# -*- coding: ascii -*-
"""
Interface usage test.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import unittest

from examples.stream_setup import SimplePacket, COBSStreamFramingCodec

from embutils.serial import Interface, Stream, Device
from embutils.utils import SDK_LOG


# -->> Definitions <<------------------
SDK_LOG.enable()


# -->> Test API <<---------------------
class TestFrameInterface(unittest.TestCase):
    """
    Basic streaming tests using the SimplePacket example.
    """
    def test_transmit(self):
        """
        Send and receive an item using the stream on a looped serial device.
        Test if the transmitted/received items are the same.
        """
        item = SimplePacket(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))
        self.transmit(item=item)

    @staticmethod
    def transmit(item: SimplePacket) -> None:
        """
        Simulate a serial device on loop mode and perform a comparison between
        the data being received and sent.
        """
        # Prepare interface
        sd = Device(looped=True)
        ss = Stream(device=sd, codec=COBSStreamFramingCodec(dtype=SimplePacket))
        si = Interface(stream=ss)

        # Transmission reception logic
        def rx_logic(recv: SimplePacket) -> bool:
            nonlocal item
            assert (item is not None) and (recv is not None)
            assert item == recv
            return True

        # Manage connection
        def on_connected():
            si.transmit(send=item, logic=rx_logic)
            si.stop()

        # Perform transmission
        si.on_connect += on_connected

        # Wait until ready
        si.join()


# -->> Test Execution <<---------------
if __name__ == '__main__':
    unittest.main()
