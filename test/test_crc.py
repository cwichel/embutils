import unittest
from embutils.utils.check import CRC


# Test Definitions ==============================
class TestByte(unittest.TestCase):
    """Check the CRC utility.
    """
    def test_crc4_itu(self):
        gen = CRC(name='CRC-4/ITU', size=4,
                  poly=0x03, crc_init=0x00, xor_out=0x00,
                  rev_in=True, rev_out=True
                  )
        val = gen.compute(data=bytearray("123456789", encoding="utf-8"))
        assert val == 0x07

    def test_crc5_epc(self):
        gen = CRC(name='CRC-5/EPC', size=5,
                  poly=0x09, crc_init=0x09, xor_out=0x00
                  )
        val = gen.compute(data=bytearray("123456789", encoding="utf-8"))
        assert val == 0x00

    def test_crc5_usb(self):
        gen = CRC(name='CRC-5/USB', size=5,
                  poly=0x05, crc_init=0x1F, xor_out=0x1F,
                  rev_in=True, rev_out=True
                  )
        val = gen.compute(data=bytearray("123456789", encoding="utf-8"))
        assert val == 0x19

    def test_crc8(self):
        gen = CRC(name='CRC-8', size=8,
                  poly=0x07, crc_init=0x00, xor_out=0x00
                  )
        val = gen.compute(data=bytearray("123456789", encoding="utf-8"))
        assert val == 0xF4

    def test_crc8_ebu(self):
        gen = CRC(name='CRC-8/EBU', size=8,
                  poly=0x1D, crc_init=0xFF, xor_out=0x00,
                  rev_in=True, rev_out=True
                  )
        val = gen.compute(data=bytearray("123456789", encoding="utf-8"))
        assert val == 0x97

    def test_crc16_ccit_false(self):
        gen = CRC(name='CRC-16/CCIT-FALSE', size=16,
                  poly=0x1021, crc_init=0xFFFF, xor_out=0x0000
                  )
        val = gen.compute(data=bytearray("123456789", encoding="utf-8"))
        assert val == 0x29B1

    def test_crc16_maxim(self):
        gen = CRC(name='CRC-16/MAXIM', size=16,
                  poly=0x8005, crc_init=0x0000, xor_out=0xFFFF,
                  rev_in=True, rev_out=True
                  )
        val = gen.compute(data=bytearray("123456789", encoding="utf-8"))
        assert val == 0x44C2

    def test_crc32(self):
        gen = CRC(name='CRC-32', size=32,
                  poly=0x04C11DB7, crc_init=0xFFFFFFFF, xor_out=0xFFFFFFFF,
                  rev_in=True, rev_out=True
                  )
        val = gen.compute(data=bytearray("123456789", encoding="utf-8"))
        assert val == 0xCBF43926

    def test_crc32_posix(self):
        gen = CRC(name='CRC-32/POSIX', size=32,
                  poly=0x04C11DB7, crc_init=0x00000000, xor_out=0xFFFFFFFF
                  )
        val = gen.compute(data=bytearray("123456789", encoding="utf-8"))
        assert val == 0x765E7680


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
