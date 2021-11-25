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

    #: Version major
    major: int = attr.ib(default=99, converter=int)
    #: Version minor
    minor: int = attr.ib(default=0, converter=int)
    #: Version build
    build: int = attr.ib(default=0, converter=int)

    def __str__(self) -> str:
        """
        Version as string: major.minor.build
        """
        return f"{self.major}.{self.minor}.{self.build}"

    @staticmethod
    def parse(text: TPAny) -> 'Version':
        """
        Parses a version string.

        :param TPAny text: Version string.

        :return: Version number.
        :rtype: Version

        :raises ValueError: Input is not a string or contents don't match a version pattern.
        """
        # Avoid not compatible types
        if not isinstance(text, TPText.__constraints__):
            raise ValueError(f"Parameter with value '{text}' can't be converted to text.")

        # Convert to text
        text = text if isinstance(text, str) else text.decode(errors="ignore")
        text.strip()

        # Find and parse version
        match = Version.REGEX_VER.search(string=text)
        if match is None:
            raise ValueError(f"Unable to parse a valid version number from '{text}'.")

        # Parse version
        major, minor, build = map(lambda x: int(x) if x.isdigit() else x, match.group().lower().split('.'))
        if isinstance(build, str):
            match = Version.REGEX_HEX.search(string=build)
            build = 0 if (match is None) else int(match.group(), 16)
        return Version(major=major, minor=minor, build=build)
