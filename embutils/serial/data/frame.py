#!/usr/bin/python
# -*- coding: ascii -*-
"""
Frame implementation classes.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from abc import abstractmethod
from embutils.serial.core import SerialDevice
from embutils.utils import EventHook, Serialized


class Frame(Serialized):
    """
    Frame structure implementation. This class define the base structure of a
    serializable frame object.
    """
    def __repr__(self) -> str:
        """
        Representation string.

        :returns: Representation string.
        :rtype: str
        """
        return f'{self.__class__.__name__}(raw=0x{self.raw().hex()})'

    def __eq__(self, other: 'Frame'):
        """
        Check if two objects are equal.

        :param Frame other: Instance of class to compare.

        :returns: True if equal, false otherwise.
        :rtype: bool
        """
        return self.raw() == other.raw()

    def __ne__(self, other: 'Frame'):
        """
        Check if two objects are not equal.

        :param Frame other: Instance of class to compare.

        :returns: True if not equal, false otherwise.
        :rtype: bool
        """
        return not self.__eq__(other=other)

    @abstractmethod
    def raw(self) -> bytearray:
        """
        Not encoded frame bytes.

        :returns: Frame bytes.
        :rtype: bytearray
        """
        pass


class FrameHandler:
    """
    Frame handler implementation. This class define how to process the bytes
    received from the serial device in order to deserialize a frame.
    """
    @abstractmethod
    def read_process(self, serial: SerialDevice, emitter: EventHook) -> bool:
        """
        This method implements the frame reading process.

        :param SerialDevice serial: Serial device from where the bytes are read.
        :param EventHook emitter:   Event to be raised when a frame is received.

        :returns: True if success, false on serial device disconnection or reading issues.
        :rtype: bool
        """
        pass
