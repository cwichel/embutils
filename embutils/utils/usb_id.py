#!/usr/bin/python
# -*- coding: ascii -*-
"""
USB device ID.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

import re
from typing import Tuple
from embutils.utils.bytes import bitmask


class UsbID(int):
    """USB ID implementation.
    This class represent the USB VID/PID values.
    """
    ID_MASK     = bitmask(bit=(16 - 1), fill=True)
    ID_PATTERN  = '(?:[0-9a-f]{4}):(?:[0-9a-f]{4})'

    def __new__(cls, vid: int = 0x0000, pid: int = 0x0000) -> 'UsbID':
        """Generate a new integer item with the USB ID values.

        Args:
            vid (int): Vendor ID.
            pid (int): Product ID.

        Returns:
            UsbID: USB ID instance.
        """
        # Define values
        uid = UsbID._pack(vid=vid, pid=pid)
        _vid, _pid = UsbID._unpack(value=uid)

        # Generate item
        obj = int.__new__(cls, uid)
        obj._vid = _vid
        obj._pid = _pid
        return obj

    def __repr__(self) -> str:
        """Get the class representation string.

        Return:
            str: Class representation string.
        """
        return '<{}: vid=0x{:04X}, pid=0x{:04X}>'.format(self.__class__.__name__, self._vid, self._pid)

    def __str__(self) -> str:
        """Get the class as a string.

        Return:
            str: Class string.
        """
        return 'VID:PID={:04X}:{:04X}'.format(self._vid, self._pid)

    @property
    def vid(self) -> int:
        """Get the VID value.

        Return:
            int: VID value.
        """
        return self._vid

    @property
    def pid(self) -> int:
        """Get the PID value.

        Return:
            int: PID value.
        """
        return self._pid

    @property
    def vid_as_hex(self) -> str:
        """Get the VID value as hex.

        Returns:
            str: String with the hex value.
        """
        return '0x{:02X}'.format(self._vid)

    @property
    def pid_as_hex(self) -> str:
        """Get the PID value as hex.

        Returns:
            str: String with the hex value.
        """
        return '0x{:02X}'.format(self._pid)

    @staticmethod
    def from_int(uid: int) -> 'UsbID':
        """Unpacks the USB ID from a integer.

        Args:
            uid (int): USB ID (based on VID/PID).

        Returns:
            UsbID: Object with VID/PID based on input.
        """
        vid, pid = UsbID._unpack(value=uid)
        return UsbID(vid=vid, pid=pid)

    @staticmethod
    def from_str(uid: str) -> 'UsbID':
        """Unpacks the USB ID from a string.

        Args:
            uid (str): USB ID (based on VID/PID) with format VID:PID.

        Returns:
            UsbID: Object with VID/PID based on input.
        """
        match = re.findall(pattern=UsbID.ID_PATTERN, string=uid.lower())
        if match:
            return UsbID.from_int(uid=int(match[0].replace(':', ''), 16))
        raise ValueError('Invalid USB ID: {}'.format(uid))

    @staticmethod
    def _pack(vid: int, pid: int) -> int:
        """Pack the VID and UID values into an int.

        Args:
            vid (int): Vendor ID.
            pid (int): Product ID.

        Returns:
            int: Combined VID/PID value.
        """
        pid = UsbID.ID_MASK & pid
        vid = UsbID.ID_MASK & vid
        return (vid << 16) | pid

    @staticmethod
    def _unpack(value: int) -> Tuple[int, int]:
        """Unpack the VID and PID values from an int.

        Args:
            value (int): Combined VID/PID value.

        Returns:
            int, int: VID, PID values.
        """
        pid = UsbID.ID_MASK & value
        vid = UsbID.ID_MASK & (value >> 16)
        return vid, pid
