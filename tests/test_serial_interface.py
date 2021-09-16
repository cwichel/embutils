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

from embutils.serial import Interface
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
        si = Interface(codec=COBSStreamFramingCodec(dtype=SimplePacket), looped=True)

        # Transmission reception logic
        def rx_logic(recv: SimplePacket) -> bool:
            nonlocal item
            assert (item is not None) and (recv is not None)
            assert item == recv
            return True

        # Perform transmission
        si.transmit(send=item, logic=rx_logic)

        # Wait until ready
        si.stop()
        si.join()


# -->> Test Execution <<---------------
if __name__ == '__main__':
    unittest.main()
