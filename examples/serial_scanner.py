#!/usr/bin/python
# -*- coding: ascii -*-
"""
Serial scanner usage example.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from embutils.serial import DeviceList, DeviceScanner
from embutils.utils import SDK_LOG
import time


# Example Definitions ===========================
def on_change_handler(event: DeviceScanner.Event, dev_diff: DeviceList) -> None:
    """
    Process the serial device change event.

    :param SerialDeviceScanner.Event event: Serial device scanner Event.
    :param SerialDeviceList dev_diff: Event change list.
    """
    dev = '\r\n\t'.join(f'{item}' for item in dev_diff)
    msg = f'{event.__repr__()}\r\n\t{dev}'
    print(msg)


def ex_serial_scanner() -> None:
    """
    Serial scanner example.

    In this example we:

    #. Create a serial device scanner.
    #. Set a callback function to print changes on the connected serial devices.

    """
    # Create a serial scanner instance
    ss = DeviceScanner(period=0.05)
    ss.on_list_change += on_change_handler

    # Maintain this alive
    while True:
        time.sleep(0.01)


# Example Execution =============================
if __name__ == '__main__':
    SDK_LOG.enable()
    ex_serial_scanner()
