import time
import unittest
from embutils.serial_process.core import SerialDevice, FrameStream
from embutils.utils.common import UsbID
from examples.ex_frame import SimpleFrame, SimpleFrameHandler


# Test Definitions ==============================
class TestFrameStream(unittest.TestCase):
    """Basic streaming tests using the SimpleFrame example.
    """
    def test_send_and_receive(self):
        """Send and receive a frame using the frame stream on a looped serial device.
        Test if the transmitted/received frames are the same.
        """
        frame = SimpleFrame(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))
        self.send_and_receive(frame_tx=frame)

    @staticmethod
    def send_and_receive(frame_tx: SimpleFrame) -> None:
        """Simulate a serial device on loop mode and perform a comparison between
        the data being received and sent.
        """
        # Stop flag
        is_ready = False

        # Manage frame reception
        def on_frame_received(frame: SimpleFrame):
            nonlocal frame_tx, is_ready
            assert frame is not None
            assert frame_tx == frame
            is_ready = True

        # Initialize frame stream
        fh = SimpleFrameHandler()
        sd = SerialDevice(usb_id=UsbID(vid=0x1234, pid=0x5678), looped=True)
        fs = FrameStream(serial_device=sd, frame_handler=fh)
        fs.on_frame_received += on_frame_received

        # Send frame
        fs.send_frame(frame=frame_tx)

        # Maintain alive the process
        while not is_ready:
            time.sleep(0.1)


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
