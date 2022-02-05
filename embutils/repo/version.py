#!/usr/bin/python
# -*- coding: ascii -*-
"""
Version handler class.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import abc
import datetime as dt
import os

import attr

from ..utils.common import ENCODE, TPPath
from ..utils.math import closest_multi
from ..utils.path import Path, FileTypeError
from ..utils.subprocess import execute
from ..utils.version import Version


# -->> Tunables <<---------------------


# -->> Definitions <<------------------
#: Source path
PATH_THIS = Path(os.path.abspath(os.path.dirname(__file__)))
#: TeMPLate path
PATH_TMPL = PATH_THIS / "templates"


# -->> API <<--------------------------
class AbstractVersionExporter(abc.ABC):
    """
    Version exporter abstraction.
    This class implements the logic used to export the version to any language.
    """
    @abc.abstractmethod
    def export(self, version: Version, path: TPPath, author: str = "Unknown") -> None:
        """
        Exports the version to be used on a given language.

        :param Version version: Version to be exported.
        :param TPPath path:     Target file path.
        :param str author:      Exported file owner.
        """


class AbstractVersionUpdater(abc.ABC):
    """
    Version updater abstraction.
    This class implements the logic to update the version number.
    """
    @abc.abstractmethod
    def update(self, version: Version, path: TPPath) -> None:
        """
        Updates the version number.

        :param Version version: Version to be exported.
        :param TPPath path:     Target file path.
        """


class AbstractVersionStorage(abc.ABC):
    """
    Version storage abstraction.
    This class implements the logic to store/retrieve the base version number.
    """
    @abc.abstractmethod
    def load(self, version: Version, path: TPPath) -> None:
        """
        Loads the version info from the given file.

        :param Version version: Version that will be updated after load.
        :param TPPath path:     Source file path.
        """

    @abc.abstractmethod
    def save(self, version: Version, path: TPPath) -> None:
        """
        Saves the version info on the given file.

        :param Version version: Version to be stored.
        :param TPPath path:     Target file path.
        """


@attr.s
class VersionHandler(Version):
    """
    Version handler implementation.

    Yse this class to perform operations over the version number.
    """
    #: Handler used to export the version number.
    exporter:   AbstractVersionExporter = attr.ib(default=None)
    #: Handler used to save/load the version number.
    storage:    AbstractVersionStorage  = attr.ib(default=None)
    #: Handler used to update the version number.
    updater:    AbstractVersionUpdater  = attr.ib(default=None)

    def save(self, path: TPPath = os.getcwd()) -> None:
        """
        Stores the version number on the given path.

        :param TPPath path:     Target file path.
        """
        # Check handler existence
        if self.storage is None:
            raise RuntimeError("Version storage handler not provided!")
        # Execute
        self.storage.save(version=self, path=path)

    def load(self, path: TPPath = os.getcwd()) -> None:
        """
        Retrieves the version number from the given path.

        :param TPPath path:     Source file path.
        """
        # Check handler existence
        if self.storage is None:
            raise RuntimeError("Version storage handler not provided!")
        # Execute
        self.storage.load(version=self, path=path)

    def update(self, path: TPPath = os.getcwd()) -> None:
        """
        Updates the version number.

        :param TPPath path:     Source file path.
        """
        # Check handler existence
        if self.updater is None:
            raise RuntimeError("Version updater handler not provided!")
        # Execute
        self.updater.update(version=self, path=path)

    def export(self, path: TPPath = os.getcwd(), author: str = "Unknown") -> None:
        """
        Exports the version number.

        :param TPPath path:     Target file path.
        :param str author:      Target file owner.
        """
        # Check handler existence
        if self.exporter is None:
            raise RuntimeError("Version exporter handler not provided!")
        # Execute
        self.exporter.export(version=self, path=path, author=author)


class CCppVersionExporter(AbstractVersionExporter):
    """
    C/C++ Version Exporter.
    Implements the logic to export the version number to a C/C++ header file
    """
    #: Item print size.
    ITEMSIZE = 20
    #: Default exported version filename.
    FILENAME = "version.h"
    #: Supported header file extensions.
    SUFFIXES = [".h", ".hpp"]
    #: C/C++ header template.
    TEMPLATE = PATH_TMPL / "template_version_c.h"

    def export(self, version: Version, path: TPPath, author: str = "Unknown") -> None:
        """
        Exports the version number to a C/C++ header using a header template.

        :param Version version: Version to be exported.
        :param TPPath path:     Target file path.
        :param str author:      Exported file owner.
        """
        # Check file
        path = Path.validate_file(path=path, none_ok=False, default=self.FILENAME)
        if path.suffix.lower() not in self.SUFFIXES:
            raise FileTypeError(f"Header path doesnt have the right suffix ({self.SUFFIXES}): {path}.")

        # Generate header
        with path.open(mode="w", encoding=ENCODE) as file:
            tmpl = self.TEMPLATE.open(mode="r", encoding=ENCODE).read()
            file.write(tmpl.format(
                file=path.name, author=author,
                guard=f"_{path.stem}_H_".upper(),
                date=f"{dt.datetime.now().strftime('%m/%d/%Y %H:%M:%S')}",
                major=self._format(item=version.major),
                minor=self._format(item=version.minor),
                build=self._format(item=version.build),
                version=f"{version}"
                ))

    def _format(self, item: int) -> str:
        """
        Formats the version number item.

        :param int item: Version item value.

        :return: Item entry.
        :rtype: str
        """
        hexval = f"0x{item:0{closest_multi(ref=len(hex(item)[2:]), base=2)}X}U"
        return f"{hexval:{self.ITEMSIZE}s}   /* DEC: {str(item):<{self.ITEMSIZE}s} */"


class SimpleVersionStorage(AbstractVersionStorage):
    """
    Simple Version Storage.
    Stores and load the version number on a simple text file.
    """
    #: Default version storage filename.
    FILENAME = "version.txt"

    def load(self, version: Version, path: TPPath) -> None:
        """
        Loads the version number from a text file.

        :param Version version: Version to be loaded.
        :param TPPath path:     Path from which the version will be loaded.
        """
        # Check file
        path = Path.validate_file(path=path, none_ok=False, must_exist=True, default=self.FILENAME)

        # Load version from file
        with path.open(mode="r", encoding=ENCODE) as file:
            version.parse(text=file.read())

    def save(self, version: Version, path: TPPath) -> None:
        """
        Saves the version number as text.

        :note: This operation re-writes the target file to only store the version number.

        :param Version version: Version to be stored.
        :param TPPath path:     Path in which the version will be stored.
        """
        # Check file
        path = Path.validate_file(path=path, none_ok=False, default=self.FILENAME)

        # Store version string
        with path.open(mode="w", encoding=ENCODE) as file:
            file.write(f"{version}")


class GitBuildVersionUpdater(AbstractVersionUpdater):
    """
    Git Version Updater.
    Implements the logic to retrieve to update the version build number based on
    the latest Git commit.
    """
    #: No repo version build number.
    NO_BUILD = 999999

    def update(self, version: Version, path: TPPath) -> None:
        """
        Updates the version build number based on the latest Git commit.

        :param Version version: Version to be updated.
        :param TPPath path:     Path in which the repository is initialized.
        """
        # Update the build number with the commit number
        ret = execute(cmd="git rev-parse --short HEAD", cwd=path, pipe=False)
        ret = (ret.stderr + ret.stdout).lower().strip()
        version.build = self.NO_BUILD if ("not a git" in ret) else int(ret, 16)


# -->> Export <<-----------------------
__all__ = [
    "AbstractVersionExporter",
    "AbstractVersionStorage",
    "AbstractVersionUpdater",
    "VersionHandler",
    "CCppVersionExporter",
    "SimpleVersionStorage",
    "GitBuildVersionUpdater",
    ]
