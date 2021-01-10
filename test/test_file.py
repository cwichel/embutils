import os
import unittest
from pathlib import Path
from embutils.utils.files import BinaryFile


# Test Definitions ==============================
class TestByte(unittest.TestCase):
    """Check the files implementation.
    """
    _root = Path(os.path.dirname(os.path.abspath(__file__)))
    _file = (_root / 'test.bin')
    _bin_file = BinaryFile(path=_file)
    _bin_data = bytearray([0x31, 0x32, 0x33, 0x34, 0x35])

    def test_01_read_write(self):
        # Remove old file
        self._bin_file.remove()
        assert not self._bin_file.exist

        # Write data
        self._bin_file.write(data=self._bin_data)
        assert self._bin_file.exist

        # Check
        data = self._bin_file.read()
        assert data == self._bin_data

    def test_02_truncate(self):
        # Truncate existing file
        self._bin_file.truncate(mod=16)

        # Check size
        data = self._bin_file.read()
        size = len(data)
        assert (size % 16) == 0
        assert data[:len(self._bin_data)] == self._bin_data
        assert sum(data[len(self._bin_data):]) == 0

    def test_03_remove(self):
        # Check that the file exists
        assert self._bin_file.exist

        # Remove and check
        self._bin_file.remove()
        assert not self._bin_file.exist


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
