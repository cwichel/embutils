#!/usr/bin/env python
##
# @file       serialized.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Simple abstraction for serialized items.
# =============================================================================

from abc import abstractmethod


class Serialized:
    """Serial item abstract definition.
    """
    LENGTH = 0

    @property
    def length(self) -> int:
        """Length of the payload contents.

        Returns:
            int: Payload length
        """
        return self.LENGTH

    @abstractmethod
    def serialize(self) -> bytearray:
        """Serialize the item to a bytearray.

        Returns:
            bytearray: Serialized object.
        """
        pass

    @staticmethod
    @abstractmethod
    def deserialize(data: bytearray) -> 'Serialized':
        """Deserializes an item form the input bytes.

        Args:
            data (bytearray): Input byte stream.

        Returns:
            SerialItem: Deserialized item.
        """
        pass
