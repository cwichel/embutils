#!/usr/bin/python
# -*- coding: ascii -*-
"""
USB device ID.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import re
from typing import Tuple
from embutils.utils.bytes import bitmask


class UsbID(int):
    """
    USB ID implementation. This class represents the USB VID/PID as a single
    integer value.
    """
    #: Define a bitmask to filter and format the PID/VID values.
    ID_MASK = bitmask(bit=(16 - 1), fill=True)

    #: Define a regular expression pattern for USB ID parsing.
    ID_PATTERN = '(?:[0-9a-f]{4}):(?:[0-9a-f]{4})'

    def __new__(cls, vid: int = 0x0000, pid: int = 0x0000) -> 'UsbID':
        """
        Creates an integer instance that allows to parse the VID and PID values.

        :args int vid: Vendor ID number.
        :args int pid: Product ID number.

        :returns: USB ID instance.
        :rtype: UsbID
        """
        # Define values
        uid = UsbID._pack(vid=vid, pid=pid)
        _vid, _pid = UsbID._unpack(uid=uid)

        # Generate item
        obj = int.__new__(cls, uid)
        obj._vid = _vid
        obj._pid = _pid
        return obj

    def __repr__(self) -> str:
        """
        Representation string.

        :returns: Representation string.
        :rtype: str
        """
        return f'{self.__class__.__name__}(vid=0x{self.vid:04X}, pid=0x{self.pid:04X})'

    def __str__(self) -> str:
        """
        Class object as string.

        :returns: Object value string.
        :rtype: str
        """
        return f'VID:PID={self._vid:04X}:{self._pid:04X}'

    @property
    def vid(self) -> int:
        """
        USB VID value.

        :returns: VID value.
        :rtype: int.
        """
        return self._vid

    @property
    def pid(self) -> int:
        """
        USB PID value.

        :returns: PID value.
        :rtype: int.
        """
        return self._pid

    @staticmethod
    def from_int(uid: int) -> 'UsbID':
        """
        Unpacks the USB ID from an int.

        :param int uid: USB ID in int format.

        :returns: USB ID object.
        :rtype: UsbID
        """
        vid, pid = UsbID._unpack(uid=uid)
        return UsbID(vid=vid, pid=pid)

    @staticmethod
    def from_str(uid: str) -> 'UsbID':
        """
        Unpacks the USB ID from a string.

        :param str uid: USB ID in string format (VID:PID).

        :raises ValueError: Input doesnt match the expected format.

        :returns: USB ID object.
        :rtype: UsbID
        """
        match = re.findall(pattern=UsbID.ID_PATTERN, string=uid.lower())
        if match:
            return UsbID.from_int(uid=int(match[0].replace(':', ''), 16))
        raise ValueError(f'Invalid USB ID: {uid}')

    @staticmethod
    def _pack(vid: int, pid: int) -> int:
        """
        Pack the VID/PID into an int value.

        :args int vid: Vendor ID number.
        :args int pid: Product ID number.

        :returns: Packed USB ID value.
        :rtype: int
        """
        pid = UsbID.ID_MASK & pid
        vid = UsbID.ID_MASK & vid
        return (vid << 16) | pid

    @staticmethod
    def _unpack(uid: int) -> Tuple[int, int]:
        """
        Unpacks the VID/PID from an int value.

        :param int uid: Packed USB ID value.

        :returns: VID, PID
        :rtype: Tuple[int, int]
        """
        pid = UsbID.ID_MASK & uid
        vid = UsbID.ID_MASK & (uid >> 16)
        return vid, pid
