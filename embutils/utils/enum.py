#!/usr/bin/python
# -*- coding: ascii -*-
"""
Enumeration utilities.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

from enum import IntEnum


class IntEnumMod(IntEnum):
    """Modified IntEnum class.
    """
    def __repr__(self) -> str:
        """Get the class representation string.

        Return:
            str: Class representation string.
        """
        return f'{self.__class__.__name__}({self.__str__()})'

    def __str__(self) -> str:
        """Get the value as string.

        Return:
            str: Enum value as string.
        """
        return f'{self.name}(0x{self.value:X})'

    @classmethod
    def from_int(cls, value: int) -> 'IntEnumMod':
        """If available, convert the input to a enum object.

        Args:
            value (int): Item to be converted.

        Returns:
            IntEnumMod: Enumeration object.
        """
        if cls.has_value(value=value):
            return cls(value)
        else:
            raise ValueError("Value 0x{:02X} is not defined.".format(value))

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Get if the given value exists on the class.

        Args:
            value (int): Item to check.

        Returns:
            bool: True if exists, false otherwise.
        """
        return value in cls._value2member_map_
