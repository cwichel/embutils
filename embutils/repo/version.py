#!/usr/bin/python
# -*- coding: ascii -*-
"""
Define the version handler class

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
import abc
import datetime
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Union


# -->> Definitions <<------------------
THIS = Path(os.path.abspath(os.path.dirname(__file__)))


# -->> API <<--------------------------
@dataclass
class Version:
    """
    Firmware version definition class.
    """
    #: Defines the structure of the version string.
    _REGEX = re.compile(pattern=r'^\d+(\.\d+){1,2}$')
    #: Version base file name.
    _VFILE = 'version.txt'
    #: Default build number.
    _BUILD = 99999

    #: Version major.
    major: int = 99
    #: Version minor.
    minor: int = 0
    #: Version build.
    build: Union[None, int] = None

    def __str__(self):
        """
        Version as string: major.minor.build
        """
        return f'{self.major}.{self.minor}.{self.build}'

    def bump_version(self, ver: str) -> None:
        """
        Bumps the version number.

        :param str ver: This value can be:

            - 'major': Increases the major number in 1.
            - 'minor': Increases the minor number in 1.
            - 'M.m'  : Set the major and minor numbers.

        """
        ver = ver.lower()
        if ver ==  'major':
            self.major += 1
        elif ver == 'minor':
            self.minor += 1
        elif self._REGEX.match(string=ver):
            tmp = ver.split(sep='.')
            self.major = int(tmp[0])
            self.minor = int(tmp[1])
        else:
            raise ValueError(f'Provided string is not a compatible version option: {ver}')

    def load_version(self, path: Path) -> 'Version':
        """
        Loads the version number from a 'version.txt' file. The version number needs to be
        in the format 'major.minor.build'.

        :param Path path: Path were the version text file is stored.
        """
        if not (path.is_dir() and path.exists()):
            raise ValueError(f'The provided path is not reachable: {path}')

        file = path / self._VFILE
        if not file.exists():
            raise ValueError(f'Unable to find a version.txt file in: {path}')

        with file.open(mode='r') as ver_file:
            ver = ver_file.read().split('.')
            self.major = int(ver[0])
            self.minor = int(ver[1])
            self.build = int(ver[2]) if (ver[2].upper() != 'X') else None
        return self

    def save_version(self, path: Path, store_build: bool = False) -> None:
        """
        Stores the version number to 'version.txt' file. The version number will be stored
        in the format 'major.minor.build'.

        :param Path path: Path were the version text file will be stored.
        :param bool store_build: If true, the build value will be stored in the file. False by default.
        """
        if not (path.is_dir() and path.exists()):
            raise ValueError(f'The provided path is not reachable: {path}')

        file = path / self._VFILE
        with file.open(mode='w') as ver_file:
            build = self.build if (store_build and self.build is not None) else 'X'
            ver_file.write(f'{self.major}.{self.minor}.{build}')

    def export_c(self, author: str, note: str, file: Path) -> None:
        if file.parent.exists() and file.parent.is_dir():
            template = (THIS / 'version_template.h').open(mode='r').read()
            template = template.format(
                file=file.name, author=author, note=note, date=f'{datetime.datetime.now():%x %X}',
                major=self.major, minor=self.minor,
                build=f'0x{self.build:X}',
                version=f'"{self.major}.{self.minor}.{self.build}"'
                )
            file.open('w').write(template)

    @abc.abstractmethod
    def get_build(self, path: Path = Path(os.getcwd())) -> None:
        """
        Get the build number.

        :param Path path: Not used.
        """
        _ = path
        self.build = self._BUILD


class VersionGit(Version):
    """
    Git version specialization.
    """
    def get_build(self, path: Path = Path(os.getcwd())) -> None:
        """
        Get the build number from the commit short ID number.

        :param Path path: Path to the Git repository.
        """
        cmd = f'cd {path} && git rev-parse --short HEAD'
        ver = subprocess.check_output(cmd, shell=True).decode()
        if 'not a git' in ver.lower():
            self.build = self._BUILD
        else:
            self.build = int(ver, 16)


class VersionSVN(Version):
    """
    SVN version specialization.
    """
    def get_build(self, path: Path = Path(os.getcwd())) -> None:
        """
        Get the build number from the SVN revision number.

        :param Path path: Path to the SVN repository.
        """
        cmd = f'svnversion {path}'
        ver = subprocess.check_output(cmd, shell=True).decode()
        if 'unversioned directory' in ver.lower():
            self.build = self._BUILD
        else:
            tmp = re.findall(pattern=r'\d+', string=ver)
            self.build = int(tmp[-1])
