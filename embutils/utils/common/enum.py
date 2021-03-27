#!/usr/bin/env python
##
# @file       enum.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Custom enumeration class alternatives.
# =============================================================================

from enum import IntEnum
from embutils.utils.common.logger import LOG_SDK


logger_sdk = LOG_SDK.logger


class IntEnumMod(IntEnum):
    """Modified IntEnum class.
    """
    def __repr__(self) -> str:
        """Get the class representation string.

        Return:
            str: Class representation string.
        """
        return '<{name}: {cmd_name}(0x{cmd_value:X})>'.format(
            name=self.__class__.__name__,
            cmd_name=self.name,
            cmd_value=self.value
            )

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
            msg = "Value 0x{:02X} is not defined.".format(value)
            logger_sdk.error(msg)
            raise ValueError(msg)

    @classmethod
    def has_value(cls, value: int) -> bool:
        """Get if the given value exists on the class.

        Args:
            value (int): Item to check.

        Returns:
            bool: True if exists, false otherwise.
        """
        return value in cls._value2member_map_
