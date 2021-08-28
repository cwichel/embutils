#!/usr/bin/python
# -*- coding: ascii -*-
"""
Serialized object abstract implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional


# -->> Definitions <<------------------


# -->> API <<--------------------------
class AbstractSerialized(ABC):
    """
    Serialized abstraction.
    This class implements the expected interface for a serialized object.
    """
    def __repr__(self) -> str:
        """
        Representation string.
        """
        return f'{self.__class__.__name__}(serialized=0x{self.serialize().hex()})'

    def __eq__(self, other: object) -> bool:
        """
        Check if the object is equal to the input.
        """
        if isinstance(other, self.__class__):
            return self.serialize() == other.serialize()
        return False

    def __ne__(self, other: object):
        """
        Check if the object is different to the input.
        """
        return not self.__eq__(other)

    @abstractmethod
    def serialize(self) -> bytearray:
        """
        Serializes the item into a bytearray.

        :returns: Serialized object.
        :rtype: bytearray.
        """
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytearray) -> Tuple[bytearray, Optional['AbstractSerialized']]:
        """
        Deserializes an object from a bytearray.

        :param bytearray data: Data to extract the object from.

        :returns: Tuple containing:

            - Bytes remaining from process.
            - Deserialized object if available, None otherwise.

        :rtype: Tuple[bytearray, Optional['AbstractSerialized']]
        """
        pass
