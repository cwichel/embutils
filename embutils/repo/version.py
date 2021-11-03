#!/usr/bin/python
# -*- coding: ascii -*-
"""
Version handler class.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import datetime as dt
import os
import re

import attr

from ..utils.path import TPPath, as_path, path_validator
from ..utils.subprocess import execute


# -->> Definitions <<------------------
#: Source path
PATH_THIS = as_path(os.path.abspath(os.path.dirname(__file__)))
#: TeMPLate path
PATH_TMPL = PATH_THIS / "templates"


# -->> API <<--------------------------
@attr.s
class Version:
    """
    Firmware version definition class.
    """
    #: Unversioned build number
    UVER_BUILD = 99999

    #: Version major
    major: int = attr.ib(default=99, converter=int)
    #: Version minor
    minor: int = attr.ib(default=0, converter=int)
    #: Version build
    build: int = attr.ib(default=UVER_BUILD, converter=int)

    def __str__(self) -> str:
        """
        Version as string: major.minor.build
        """
        return f"{self.major}.{self.minor}.{self.build}"

    def update_build(self, path: TPPath) -> None:
        """
        Updates the build number for the current repo.

        :param TPPath path: Path to repo.
        """
        # Unversioned: do nothing.
        _ = path
        self.build = self.UVER_BUILD

    def save(self, path: TPPath, store_build: bool = False) -> None:
        """
        Stores the version number to the provided file.
        The version number will be stored in the format "major.minor.build".

        :param TPPath path:         Path were the version text file will be stored.
        :param bool store_build:    If true, the build will be stored. False by default.
        """
        path = path_validator(path=path, allow_none=False, check_reachable=True)
        with path.open(mode="w") as file:
            build = self.build if (store_build and self.build is not None) else "X"
            file.write(f"{self.major}.{self.minor}.{build}")

    @classmethod
    def load(cls, path: TPPath) -> "Version":
        """
        Loads the version number from the provided file.
        The version number needs to be in the format "major.minor.build".

        :param TPPath path:         Path to the version file.
        """
        path = path_validator(path=path, allow_none=False, check_reachable=True)
        with path.open(mode="r") as ver_file:
            tmp = ver_file.read().split(".")
            ver = cls(
                    major=int(tmp[0]),
                    minor=int(tmp[1]),
                    build=int(tmp[2]) if (tmp[2].upper() != "X") else Version.UVER_BUILD
                    )
            return ver


@attr.s
class VersionGit(Version):
    """
    Git version specialization.
    """
    def update_build(self, path: TPPath = os.getcwd()) -> None:
        """
        Updates the build number for the current repo.

        :param TPPath path: Path to repository.
        """
        out = execute(cmd="git rev-parse --short HEAD", cwd=f"{path}", pipe=False)
        msg = (out.stderr + out.stdout).strip().lower()
        if "not a git" in msg:
            self.build = self.UVER_BUILD
        else:
            self.build = int(msg, 16)


@attr.s
class VersionSVN(Version):
    """
    SVN version specialization.
    """

    def update_build(self, path: TPPath = os.getcwd()) -> None:
        """
        Updates the build number for the current repo.

        :param TPPath path: Path to repository.
        """
        out = execute(cmd="svnversion .", cwd=f"{path}", pipe=False)
        msg = (out.stderr + out.stdout).strip().lower()
        if "unversioned directory" in msg:
            self.build = self.UVER_BUILD
        else:
            tmp = re.findall(pattern=r"\d+", string=msg)
            self.build = int(tmp[-1])


def version_export_c(path: TPPath, ver: Version, author: str, note: str) -> None:
    """
    Exports the version to a C header file.

    :param TPPath path:     Path to store the generated C header file.
    :param Version ver:     Version instance.
    :param str author:      Author to be declared on the header file.
    :param str note:        Note to be added on the file documentation.

    """
    # Check target path
    path = path_validator(path=path, allow_none=False, check_reachable=True)

    tmpl = PATH_TMPL / "template_version_c.h"
    base = tmpl.open(mode="r").read()

    with path.open(mode="w") as file:
        file.write(base.format(
            file=path.name, author=author, note=note, date=f"{dt.datetime.now():%x %X}",
            major=ver.major, minor=ver.minor, build=f"0x{ver.build:X}",
            version=f'"{ver.major}.{ver.minor}.{ver.build}"'
            ))
