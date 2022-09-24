#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Enumeration utilities and tweaks.

:date:      2022
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

# Built-in
import enum
import typing as tp


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class IntEnum(enum.IntEnum):
    """Extends the standard enumeration class with extra utilities."""

    def __str__(self) -> str:
        return f"{self.name}(0x{self.value:X})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__str__()})"

    @classmethod
    def has_value(
        cls,
        value: tp.Union[int, str],
    ) -> bool:
        """Check if the value exists on the enum.

        :param tp.Union[int, str] value: Value to check

        :return: If true, value exists on the enum.
        :rtype: bool
        """
        return value in cls.__get_source(dtype=type(value))

    @classmethod
    def from_value(
        cls,
        value: tp.Union[int, str],
    ) -> "IntEnum":
        """Tries to get the enum item that match the provided value.

        :param tp.Union[int, str] value: Desired enum value

        :return: Enum object.
        :rtype: IntEnum
        """
        item = cls.__get_source(dtype=type(value)).get(value, None)
        if item is not None:
            return item
        raise ValueError(f"{value} is not defined on {cls.__name__}")

    @classmethod
    def __get_source(
        cls,
        dtype: tp.Type,
    ) -> dict:
        """Get item source depending on the data type.

        :param tp.Type dtype: Value data type

        :return: Enum values indexed by an object of the provided data type.
        :rtype: dict
        """
        return getattr(cls, ("_value2member_map_" if (dtype == int) else "_member_map_"))


# -->> Export <<-----------------------
#: Filter to module imports
__all__ = [
    "IntEnum",
]
