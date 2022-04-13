#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Serial scanner usage example.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from embutils.serial import DeviceList, DeviceScanner
from embutils.utils import SDK_LOG


# -->> Definitions <<------------------


# -->> API <<--------------------------
def on_change_handler(event: DeviceScanner.Event, changes: DeviceList) -> None:
    """
    Process the serial device change event.

    :param SerialDeviceScanner.Event event: Serial device scanner Event.
    :param SerialDeviceList changes: Event change list.
    """
    dev = "\r\n\t".join(f"{item}" for item in changes)
    msg = f"{event.__repr__()}\r\n\t{dev}"
    print(msg)


def ex_serial_scanner() -> None:
    """
    Serial scanner example.

    In this example we:

    #. Create a serial device scanner.
    #. Set a callback function to print changes on the connected serial devices.

    """
    # Create a serial scanner instance
    ss = DeviceScanner(period=0.5)
    ss.on_list_change += on_change_handler
    ss.join()


# -->> Execution <<--------------------
if __name__ == "__main__":
    SDK_LOG.enable()
    ex_serial_scanner()
