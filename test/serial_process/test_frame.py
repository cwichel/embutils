import unittest
from embutils.utils.check import CRC
from embutils.utils.framing import cobs_encode
from examples.ex_frame import SimpleFrame


# Test Definitions ==============================
class TestFrame(unittest.TestCase):
    """Basic reference tests using the SimpleFrame example.
    """
    def test_serialize(self):
        """Check if the serialization of a frame is being done correctly.
        """
        # By hand
        frame_raw = bytearray([0x01, 0x02, 0x02, 0xDD, 0x07])
        frame_raw.extend(CRC().compute(data=frame_raw).to_bytes(length=2, byteorder='little', signed=False))
        frame_ser = cobs_encode(data=frame_raw)

        # Frame implementation
        frame = SimpleFrame(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))

        # Compare
        assert frame_raw == frame.raw()
        assert frame_ser == frame.serialize()

    def test_deserialize(self):
        """Check if the deserialization of a frame is being done correctly.
        """
        # By hand
        frame_raw = bytearray([0x01, 0x02, 0x02, 0xDD, 0x07])
        frame_raw.extend(CRC().compute(data=frame_raw).to_bytes(length=2, byteorder='little', signed=False))
        frame_ser = cobs_encode(data=frame_raw)

        # Frame creation
        frame_2 = SimpleFrame.deserialize(data=frame_ser)

        # Compare
        assert frame_2 is not None
        assert frame_raw == frame_2.raw()

    def test_comparison(self):
        """Check if the comparison of frames is being done correctly.
        """
        # Create frames
        frame_1 = SimpleFrame(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))
        frame_2 = SimpleFrame(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))
        frame_3 = SimpleFrame(source=0x02, destination=0x01, payload=bytearray([0xDD, 0x08]))

        # Compare
        assert frame_1 is not frame_2
        assert frame_1 == frame_2
        assert frame_1.serialize() == frame_2.serialize()

        assert frame_1 != frame_3
        assert frame_1.serialize() != frame_3.serialize()


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
