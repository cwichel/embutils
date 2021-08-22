#!/usr/bin/python
# -*- coding: ascii -*-
"""
Serialized object definition.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from abc import abstractmethod
from typing import Union


class Serialized:
    """
    Abstract implementation for a serialized item.
    """
    #:  Serialized object byte length. If the length is variable, this defines the minimum.
    _LENGTH = 0

    @property
    def length(self) -> int:
        """
        Serialized item length in bytes. This property allows to handle the cases
        in which the object has variable size and the attribute :attr:`LENGTH` only
        defines the minimum length.
        """
        return self._LENGTH

    @abstractmethod
    def serialize(self) -> bytearray:
        """
        Serializes the object to a byte array.

        :returns: Serialized object.
        :rtype: bytearray
        """
        pass

    @staticmethod
    @abstractmethod
    def deserialize(data: bytearray) -> Union[None, 'Serialized']:
        """
        Deserializes the object from a byte array.

        :param bytearray data: Bytes to be deserialized.

        :returns: None if deserialization fail, deserialized object otherwise.
        :rtype: Serialized
        """
        pass
