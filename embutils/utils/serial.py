from abc import abstractmethod


class SerialItem:
    """Serial item abstract definition.
    """
    @abstractmethod
    def serialize(self) -> bytearray:
        """Serialize the item to a bytearray.

        Returns:
            bytearray: Serialized object.
        """
        pass

    @staticmethod
    @abstractmethod
    def deserialize(data: bytearray) -> 'SerialItem':
        """Deserializes an item form the input bytes.

        Args:
            data (bytearray): Input byte stream.

        Returns:
            SerialItem: Deserialized item.
        """
        pass
