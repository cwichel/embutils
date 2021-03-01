#!/usr/bin/env python
##
# @file       frame.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Frame base implementation.
#
# NOTE: The frame defines how the payload / data is being sent / encoded.
#
# =============================================================================

from abc import abstractmethod
from embutils.serial_process.core import SerialDevice
from embutils.utils.common import EventHook, Serialized


class Frame(Serialized):
    """This class define the basic structure of the frame.
    """
    def __repr__(self):
        """Get the class representation string.

        Return:
            str: Class representation string.
        """
        return '<{}: raw={}>'.format(self.__class__.__name__, self.raw().hex())

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
