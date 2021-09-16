#!/usr/bin/python
# -*- coding: ascii -*-
"""
Serialized objects stream test.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import time
import unittest

from examples.stream_setup import SimplePacket, COBSStreamFramingCodec

from embutils.serial import Device, Stream
from embutils.utils import SDK_LOG, time_elapsed


# -->> Definitions <<------------------
SDK_LOG.enable()


# -->> Test API <<---------------------
class TestStream(unittest.TestCase):
    """
    Basic streaming tests using the SimplePacket example.
    """
    def test_send_and_receive(self):
        """
        Send and receive an item using the Stream on a looped serial Device.
        Test if the transmitted/received items are the same.
        """
        item = SimplePacket(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))
        self.send_and_receive(send=item)

    @staticmethod
    def send_and_receive(send: SimplePacket) -> None:
        """
        Simulate a serial device on loop mode and perform a comparison between
        the data being sent and received.
        """
        # Stop flag
        sent = send
        is_ready = False

        # Manage reception
        def on_received(item: SimplePacket):
            nonlocal sent, is_ready
            assert (sent is not None) and (item is not None)
            assert sent == item
            is_ready = True

        # Initialize stream
        cdc = COBSStreamFramingCodec(dtype=SimplePacket)
        dev = Device(looped=True)
        sth = Stream(device=dev, codec=cdc)
        sth.on_received += on_received

        # Send item
        sth.resume()
        sth.send(item=send)

        # Maintain alive the process until check
        start = time.time()
        while not is_ready:
            time.sleep(0.1)
            # If the process hangs, fail the test
            if time_elapsed(start=start) > 1.0:
                assert False


# -->> Test Execution <<---------------
if __name__ == '__main__':
    unittest.main()
