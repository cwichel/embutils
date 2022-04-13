#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Serialized usage test.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import unittest

from examples.stream_setup import SimplePacket

from embutils.utils import CRC


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class TestSerialized(unittest.TestCase):
    """
    Basic reference tests using the SimplePacket example.
    """
    def test_01_serialize(self):
        """
        Check if the serialization is being done correctly.
        """
        # By hand
        raw = bytearray([0x01, 0x02, 0x02, 0xDD, 0x07])
        raw.extend(CRC().compute(data=raw).to_bytes(length=2, byteorder='little', signed=False))

        # Frame implementation
        item = SimplePacket(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))

        # Compare
        assert raw == item.serialize()

    def test_02_deserialize(self):
        """
        Check if the deserialization is being done correctly.
        """
        # By hand
        raw = bytearray([0x01, 0x02, 0x02, 0xDD, 0x07])
        raw.extend(CRC().compute(data=raw).to_bytes(length=2, byteorder='little', signed=False))

        # Frame creation
        item = SimplePacket.deserialize(data=raw)

        # Compare
        assert item is not None
        assert raw == item.serialize()

    def test_03_comparison(self):
        """
        Check if the comparison is being done correctly.
        """
        # Create frames
        item_1 = SimplePacket(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))
        item_2 = SimplePacket(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))
        item_3 = SimplePacket(source=0x02, destination=0x01, payload=bytearray([0xDD, 0x08]))

        # Compare
        assert item_1 is not item_2
        assert item_1 == item_2
        assert item_1.serialize() == item_2.serialize()

        assert item_1 != item_3
        assert item_1.serialize() != item_3.serialize()


# -->> Execute <<----------------------
if __name__ == '__main__':
    unittest.main()
