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
from embutils.utils.common import EventHook, Serialized


class Frame(Serialized):
    """This class define the basic structure of the frame.
    """
    def __repr__(self):
        """Get the class representation string.

        Return:
            str: Class representation string.
        """
        return '<{}: raw={}>'.format(self.__class__.__name__, self.raw.hex())

    def __eq__(self, other: 'Frame'):
        """Compare two frames.

        Returns:
            bool: True if equal, false otherwise.
        """
        return self.raw == other.raw

    def __ne__(self, other: 'Frame'):
        """Compare two frames.

        Returns:
            bool: True if not equal, false otherwise.
        """
        return not self.__eq__(other=other)

    @property
    def raw(self) -> bytearray:
        """Frame contents as bytearray (without encoding).

        Returns:
            bytearray: Frame contents.
        """
        return self._raw()

    @abstractmethod
    def _raw(self) -> bytearray:
        """Frame contents as bytearray (without encoding).

        Returns:
            bytearray: Frame contents.
        """
        pass


class FrameHandler:
    """This class define how the frame bytes are processed when received.

    The idea is to use this class to define a state machine to receive the frame.
    """
    def __init__(self):
        """Class constructor. Initializes the frame serial handler.
        """
        self._bytes_buffer = bytearray()
        self._bytes_to_read = 0

    @property
    def bytes_to_read(self) -> int:
        """Indicate the number of bytes to be read from the serial device to
        process the current frame reception.

        Return:
            int: Number of bytes to read.
        """
        return self._bytes_to_read

    @abstractmethod
    def process(self, new_bytes: bytearray, emitter: EventHook) -> None:
        """This method process the received bytes into a frame.

        Args:
            new_bytes (bytearray): Bytes to be processed.
            emitter (EventHook): Event to be raised when a frame is received.
        """
        pass
