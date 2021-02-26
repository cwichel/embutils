#!/usr/bin/env python
##
# @file       mac.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      MAC address object implementation.
# =============================================================================

import re
from typing import List, Union


class MacAddress:
    """MAC address implementation.
    """
    FMT = '^((?:(?:[0-9a-f]{2}):){5}[0-9a-f]{2})$'

    def __init__(self, value: Union[str, int, list, bytearray] = 0, byteorder: str = 'little'):
        """Class constructor. Initializes the MAC address.

        Args:
            value (Union[str, int, list, bytearray]): MAC address value.
            byteorder (str): Endianness (little, big).
        """
        # Set the attributes (default)
        self._value = '00:00:00:00:00:00'
        self._order = 'little'

        # Update value
        self.byteorder = byteorder
        self.value = value

    def __repr__(self) -> str:
        """Get the class representation string.

        Return:
            str: Class representation string.
        """
        return '<{}: address={}>'.format(self.__class__.__name__, self.value)

    @property
    def value(self) -> str:
        """Return the MAC address.

        Returns:
            str: MAC.
        """
        return self._value

    @value.setter
    def value(self, value: Union[str, int, list, bytearray] = 0):
        """Set the MAC with the given value.

        Args:
            value Union[str, int, list, bytearray]: Possible MAC inputs.
        """
        if isinstance(value, str):
            match = re.match(pattern=self.FMT, string=value, flags=re.IGNORECASE)
            if match is None:
                raise ValueError('Value \'{}\' dont have a MAC compatible pattern.'.format(value))
            self._value = value.upper()

        elif isinstance(value, int):
            self._value = ':'.join('{}{}'.format(a, b) for a, b in zip(*[iter('{:012x}'.format(value))] * 2)).upper()

        elif isinstance(value, (list, bytearray)) and (len(value) >= 6):
            data = value[:6]
            if isinstance(data[0], str):
                data = list(map(lambda x: int(x, 16), data))
            data = int.from_bytes(bytes=data, byteorder=self._order, signed=False)
            self.value = data

        else:
            raise ValueError('Input type is not compatible.')

    @property
    def as_int(self) -> int:
        """Return the MAC address as an integer.

        Returns:
            int: MAC address value.
        """
        return int(self._value.replace(':', ''), 16)

    @property
    def as_bytes(self) -> bytearray:
        """Return the MAC address as byte array.

        Returns:
            bytearray: MAC address value.
        """
        return bytearray(self.as_int.to_bytes(length=6, byteorder=self._order, signed=False))

    @property
    def as_hex_array(self) -> List[str]:
        """Return the MAC address as a HEX array.

        Returns:
            List[str]: MAC address value.
        """
        return list(map(hex, self.as_bytes))

    @property
    def byteorder(self) -> str:
        """Return the endianness configuration.

        Returns:
            str: 'little' or 'big'
        """
        return self._order

    @byteorder.setter
    def byteorder(self, value: str = 'little') -> None:
        """Set the endianness configuration.

        Args:
            value (str): Endianness (little, big).
        """
        # Check value
        if value not in ['little', 'big']:
            raise ValueError('Endianness configuration \'{}\' is not supported.'.format(value))

        # Update endianness
        if value != self._order:
            self._order = value
