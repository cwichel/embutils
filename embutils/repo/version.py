#!/usr/bin/python
# -*- coding: ascii -*-
"""
Version handler class.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import datetime
import os
import re
import subprocess

from dataclasses import dataclass
from pathlib import Path


# -->> Definitions <<------------------
PATH_THIS = Path(os.path.abspath(os.path.dirname(__file__)))


# -->> API <<--------------------------
@dataclass
class Version:
    """
    Firmware version definition class.
    """
    UVER_BUILD = 99999          #: Unversioned build number

    major: int = 99             #: Version major
    minor: int = 0              #: Version minor
    build: int = UVER_BUILD     #: Version build

    def __str__(self) -> str:
        """
        Version as string: major.minor.build
        """
        return f'{self.major}.{self.minor}.{self.build}'

    def update_build(self, path: Path) -> None:
        """
        Updates the build number for the current repo.

        :param Path path: Path to repo.
        """
        # Unversioned: do nothing.
        _ = path

    def save(self, file: Path, store_build: bool = False) -> None:
        """
        Stores the version number to the provided file.
        The version number will be stored in the format 'major.minor.build'.

        :param Path file: Path were the version text file will be stored.
        :param bool store_build: If true, the build will be stored. False by default.
        """
        if not file.parent.exists():
            raise ValueError(f'The provided path is not reachable: {file}')
        with file.open(mode='w') as ver_file:
            build = self.build if (store_build and self.build is not None) else 'X'
            ver_file.write(f'{self.major}.{self.minor}.{build}')

    @classmethod
    def load(cls, file: Path) -> 'Version':
        """
        Loads the version number from the provided file.
        The version number needs to be in the format 'major.minor.build'.

        :param Path file: Path to the version file.
        """
        if not (file.is_file() and file.exists()):
            raise ValueError(f'The provided path is not reachable: {file}')
        with file.open(mode='r') as ver_file:
            tmp = ver_file.read().split('.')
            ver = cls(
                major=int(tmp[0]),
                minor=int(tmp[1]),
                build=int(tmp[2]) if (tmp[2].upper() != 'X') else Version.UVER_BUILD
                )
            return ver


@dataclass
class VersionGit(Version):
    """
    Git version specialization.
    """
    def update_build(self, path: Path = Path(os.getcwd())) -> None:
        """
        Updates the build number for the current repo.

        :param Path path: Path to repo.
        """
        cmd = f'cd {path} && git rev-parse --short HEAD'
        ver = subprocess.check_output(cmd, shell=True).decode()
        if 'not a git' in ver.lower():
            self.build = self.UVER_BUILD
        else:
            self.build = int(ver, 16)


@dataclass
class VersionSVN(Version):
    """
    SVN version specialization.
    """
    def update_build(self, path: Path = Path(os.getcwd())) -> None:
        """
        Updates the build number for the current repo.

        :param Path path: Path to repo.
        """
        cmd = f'svnversion {path}'
        ver = subprocess.check_output(cmd, shell=True).decode()
        if 'unversioned directory' in ver.lower():
            self.build =  self.UVER_BUILD
        else:
            tmp = re.findall(pattern=r'\d+', string=ver)
            self.build = int(tmp[-1])


def export_version_c(ver: Version, author: str, note: str, file: Path) -> None:
    """
    Exports the version to a C header file.

    :param Version ver: Version instance.
    :param str author:  Author to be declared on the header file.
    :param str note:    Note to be added on the file documentation.
    :param Path file:   Path to version C header file.
    """

    if not (file.parent.exists() and file.parent.is_dir()):
        raise ValueError(f'The provided path is not reachable: {file}')

    template = (PATH_THIS / 'version_template.h').open(mode='r').read()
    template = template.format(
        file=file.name, author=author, note=note, date=f'{datetime.datetime.now():%x %X}',
        major=ver.major, minor=ver.minor,
        build=f'0x{ver.build:X}',
        version=f'"{ver.major}.{ver.minor}.{ver.build}"'
        )
    file.open('w').write(template)
