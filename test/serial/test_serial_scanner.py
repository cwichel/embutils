#!/usr/bin/python
# -*- coding: ascii -*-
##
# @file       ex_serial_scan.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Usage example for the serial device scanner.
# =============================================================================

from embutils.serial.core import SerialDeviceList, SerialDeviceScanner
import time


# Example Definitions ===========================
def on_change_handler(event: SerialDeviceScanner.Event, dev_diff: SerialDeviceList) -> None:
    """Process the serial device change event.

    Args:
        event (SerialDeviceEvent): Serial scanner event.
        dev_diff (SerialDeviceList): Change list.
    """
    dev = '\r\n\t'.join('{}'.format(item) for item in dev_diff)
    msg = '{}\r\n\t{}'.format(event.__repr__(), dev)
    print(msg)


def test_serial_scanner() -> None:
    """Example execution.
    In this example we:
        1. Create a serial device scanner.
        2. Set a callback function to print changes on the connected serial devices.
    """
    # Create a serial scanner instance
    ss = SerialDeviceScanner(scan_period=0.05)
    ss.on_list_change += on_change_handler

    # Maintain this alive
    while True:
        time.sleep(0.01)


# Example Execution =============================
if __name__ == '__main__':
    test_serial_scanner()
