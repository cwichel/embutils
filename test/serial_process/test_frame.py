import unittest
from embutils.serial_process.data import Frame
from embutils.utils.framing import cobs_encode, cobs_decode


# Frame Definitions =============================
class SimpleFrame(Frame):
    def __init__(self, command: int, payload: ):
        self._cmd



# Test Definitions ==============================
class TestFrame(unittest.TestCase):
    pass


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
