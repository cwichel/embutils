#!/usr/bin/python
# -*- coding: ascii -*-
"""
SDK logger implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import collections as coll
import logging as log

from .enum import IntEnum


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class Logger(log.Logger):
    """
    Logger implementation wrapper.
    This class simplifies the logger formatting and level definition for the SDK.
    """
    class Level(IntEnum):
        """
        Available logger message levels.
        """
        CRITICAL    = log.CRITICAL
        DEBUG       = log.DEBUG
        ERROR       = log.ERROR
        INFO        = log.INFO
        WARNING     = log.WARNING

    #: Logger entries format definition
    Format = coll.namedtuple("Format", ["style", "pattern"])

    #: Default entry format
    DEF_FMT = Format(style="{", pattern="{created:.05f}: {name:<8s}: {levelname:<8s}: {module:<20s}: {message:s}")

    def __init__(self, name: str = "", level: Level = Level.DEBUG, fmt: Format = DEF_FMT) -> None:
        """
        Logger configuration.
        Applies the log entries formatting and initial log level.

        :param str name:  Logger name.
        :param int level: Logger initial message name.
        :param Logger.Format fmt: Log entries formatting. By default :attr:`FMT_DEFAULT`.
        """
        # Initialize logger
        super().__init__(name=name, level=level)

        # Define formatter
        if fmt is None:
            fmt = self.DEF_FMT

        # Disable logger by default
        self.disable()

        # Configure format
        fmt  = log.Formatter(fmt=fmt.pattern, style=fmt.style)
        hdl = log.StreamHandler()
        hdl.setFormatter(fmt=fmt)
        self.addHandler(hdlr=hdl)

    def enable(self) -> None:
        """
        Enable logger.
        """
        self.disabled = False

    def disable(self) -> None:
        """
        Disable logger.
        """
        self.disabled = True

    def set_level(self, level: Level = Level.DEBUG) -> None:
        """
        Set the log messages level.

        :param int level: Log level.
        """
        self.setLevel(level=level)


# -->> Instances <<--------------------
#: Embutils internal logger
SDK_LOG = Logger(name="EMBUTILS")


# -->> Export <<-----------------------
__all__ = [
    "Logger",
    "SDK_LOG",
    ]
