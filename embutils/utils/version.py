#!/usr/bin/python
# -*- coding: ascii -*-
"""
Version number implementation.

:date:      2021
:author:    cwichel
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import re

import attr

from ..utils.common import TPAny, TPText

# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
@attr.s
class Version:
    """
    Simple version definition.
    """
    #: Regex version pattern.
    REGEX_VER = re.compile(pattern=r"(([0-9]*\.){2,}([a-z0-9]{1,}))", flags=re.I)
    #: Regex HEX pattern.
    REGEX_HEX = re.compile(pattern=r"^((0x){0,1}([a-f0-9]{1,}))$", flags=re.I)
    #: Regex INT pattern.
    REGEX_INT = re.compile(pattern=r"^([0-9]{1,})$", flags=re.I)

    #: Version major
    major:      int = attr.ib(default=99, converter=int)
    #: Version minor
    minor:      int = attr.ib(default=0, converter=int)
    #: Version build
    build:      int = attr.ib(default=0, converter=int)
    #: Flag. If enabled the build is parsed/printed as HEX.
    hex_build:  bool = attr.ib(default=False, converter=bool)

    def __str__(self) -> str:
        """
        Version as string: major.minor.build
        """
        return f"{self.major}.{self.minor}.{hex(self.build)[2:] if self.hex_build else self.build}"

    def parse(self, text: TPAny) -> None:
        """
        Parses a version string.

        :param TPAny text:      Version string.

        :raises ValueError: Input is not a string or contents don't match a version pattern.
        """
        # Avoid not compatible types
        if not isinstance(text, TPText.__constraints__):
            raise ValueError(f"Parameter with value '{text}' can't be converted to text.")

        # Ensure format and search
        text  = text if isinstance(text, str) else text.decode(errors="ignore")
        match = Version.REGEX_VER.search(string=text.strip())
        if match is None:
            raise ValueError(f"Unable to parse a valid version number from '{text}'.")

        # Parse: major and minor
        items = match.group().lower().split('.')
        self.major, self.minor = map(int, items[:-1])

        # Parse: build
        base  = 16 if self.hex_build else 10
        regex = self.REGEX_HEX if self.hex_build else self.REGEX_INT
        match = regex.search(string=items[-1])
        self.build = 0 if (match is None) else int(match.group(), base)

    @staticmethod
    def from_str(text: TPAny, hex_build: bool = False) -> 'Version':
        """
        Parses a version number from a string.

        :param TPAny text:      Version string.
        :param bool hex_build:  If true, assumes that the build section is in HEX format.

        :return: Version number.
        :rtype: Version

        :raises ValueError: Input is not a string or contents don't match a version pattern.
        """
        ver = Version(hex_build=hex_build)
        ver.parse(text=text)
        return ver
