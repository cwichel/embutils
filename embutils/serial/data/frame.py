#!/usr/bin/python
# -*- coding: ascii -*-
"""
Frame implementation.
This classes are used to:
    - Define the command frame payload / serialization.
    - Define how the serial device data should be read to deserialize a frame.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

from abc import abstractmethod
from embutils.serial.core import SerialDevice
from embutils.utils.common import EventHook, Serialized


class Frame(Serialized):
    """This class define the basic structure of the frame.
    """
    def __repr__(self) -> str:
        """Get the class representation string.

        Return:
            str: Class representation string.
        """
        return '<{}: raw=0x{}>'.format(self.__class__.__name__, self.raw().hex())

    def __eq__(self, other: 'Frame'):
        """Compare two frames.

        Returns:
            bool: True if equal, false otherwise.
        """
        return self.raw() == other.raw()

    def __ne__(self, other: 'Frame'):
        """Compare two frames.

        Returns:
            bool: True if not equal, false otherwise.
        """
        return not self.__eq__(other=other)

    @abstractmethod
    def raw(self) -> bytearray:
        """Frame contents as bytearray (without encoding).

        Returns:
            bytearray: Frame contents.
        """
        pass


class FrameHandler:
    """This class define how the frame bytes are processed when received.

    The idea is to use this class to define a state machine to receive the frame.
    """
    @abstractmethod
    def read_process(self, serial_device: SerialDevice, emitter: EventHook) -> bool:
        """This method implements the frame reading state machine.

        Args:
            serial_device (bytearray): Device to read the frame bytes.
            emitter (EventHook): Event to be raised when a frame is received.

        Return:
            bool: True if success, false on serial device disconnection or
            reading issues.
        """
        pass
