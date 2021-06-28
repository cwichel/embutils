#!/usr/bin/python
# -*- coding: ascii -*-
"""
Enumeration utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from enum import IntEnum


class IntEnumMod(IntEnum):
    """
    Modified integer enumeration class. This class extends the functionalities
    of the base enumeration definition.
    """
    def __repr__(self) -> str:
        """
        Representation string.

        :returns: Representation string.
        :rtype: str
        """
        return f'{self.__class__.__name__}({self.__str__()})'

    def __str__(self) -> str:
        """
        Class object as string.

        :returns: Object value string.
        :rtype: str
        """
        return f'{self.name}(0x{self.value:X})'

    @classmethod
    def from_int(cls, value: int) -> 'IntEnumMod':
        """
        Converts, if possible, the input value to an enum object.

        :param int value: Value to be converted.

        :returns: Enumeration object.
        :rtype: IntEnumMod

        :raises ValueError: Value is not contained on the enum.
        """
        if cls.has_value(value=value):
            return cls(value)
        else:
            raise ValueError(f'Value 0x{value:02X} is not defined.')

    @classmethod
    def has_value(cls, value: int) -> bool:
        """
        Checks if the input value exist on the enum definition.

        :param int value: Value to be checked.

        :returns: True if exists, false otherwise.
        :rtype: bool
        """
        return value in cls._value2member_map_
