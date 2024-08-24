#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Alternative enumerations implementations.

:date:      2024
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# --------------------------------------
__author__ = "Christian Wiche"
__version__ = "ALPHA"
# --------------------------------------

# Built-in
import enum as en
import typing as tp


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
_ET = tp.TypeVar("_ET", bound="EnumUtils")
"""Enum type variable."""


class EnumUtils:
    """Additional utility methods for enums.

    Use this as a mixin class for your enum to get the additional methods.

    Example::

        class MyEnum(EnumUtils, en.IntEnum):
            A = 0
            B = 1

    """

    @classmethod
    def from_value(
        cls: tp.Type[_ET],
        value: tp.Any,
    ) -> tp.Optional[_ET]:
        """Get the enum member for the given value.

        :param value: Value to get the enum member for.

        :return: Enum member for the given value, None if the value is not a valid member of the enum.
        """
        # Handle enums: Only from same type, assume any other as different
        if issubclass(type(value), en.Enum):
            if isinstance(value, cls):
                return value
            return None
        # Handle values: Can be name or value
        for attr in ["_member_map_", "_value2member_map_"]:
            if (item := getattr(cls, attr, {}).get(value, None)) is not None:
                return item
        return None

    @classmethod
    def has_value(
        cls: tp.Type[_ET],
        value: tp.Any,
    ) -> bool:
        """Check if the given value is a valid member of the enum.

        :param value: Value to check.

        :return: True if the value is a valid member of the enum, False otherwise.
        """
        return cls.from_value(value=value) is not None


# -->> API <<---------------------------


# -->> Export <<------------------------
__all__ = [
    "EnumUtils",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
