#!/usr/bin/python
# -*- coding: ascii -*-
"""
Frame interface usage test.
The frame interface is used to decode the serial input into a frame.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

import unittest
from embutils.examples import SimpleFrame, SimpleFrameHandler
from embutils.serial.core import SerialInterface
from embutils.utils.common import LOG_SDK


LOG_SDK.enable()


# Test Definitions ==============================
class TestFrameInterface(unittest.TestCase):
    """Basic streaming tests using the SimpleFrame example.
    """
    def test_transmit(self):
        """Send and receive a frame using the frame stream on a looped serial device.
        Test if the transmitted/received frames are the same.
        """
        frame = SimpleFrame(source=0x01, destination=0x02, payload=bytearray([0xDD, 0x07]))
        self.transmit(frame=frame)

    @staticmethod
    def transmit(frame: SimpleFrame) -> None:
        """Simulate a serial device on loop mode and perform a comparison between
        the data being received and sent.
        """
        # Prepare interface
        si = SerialInterface(frame_handler=SimpleFrameHandler(), looped=True)

        # Transmission reception logic
        def rx_logic(sent: SimpleFrame, recv: SimpleFrame) -> bool:
            assert (sent is not None) and (recv is not None)
            assert sent == recv
            return True

        # Perform transmission
        si.transmit(send=frame, resp_logic=rx_logic)

        # Wait until ready
        si.stop()
        si.join()


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
