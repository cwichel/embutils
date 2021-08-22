#!/usr/bin/python
# -*- coding: ascii -*-
"""
SDK logger implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import logging

from dataclasses import dataclass


# -->> Definitions <<------------------


# -->> API <<--------------------------
@dataclass
class LoggerFormat:
    """
    Implements a data type to define and store the logger entries formatting
    configuration.
    """
    #: Defines the structure of each log entry.
    pattern:    str = '{created:.05f}: {name:<8s}: {levelname:<8s}: {module:<20s}: {message:s}'

    #: Defines how the pattern should be interpreted.
    style:      str = '{'


class Logger:
    """
    Implements a basic logger handler class.
    """
    #: Default logger entry format.
    FMT_DEFAULT = LoggerFormat()

    def __init__(self, name: str = '', fmt: LoggerFormat = None) -> None:
        """Logger initialization. Applies the basic configuration to
        the logger.

        :param str name: Logger name.
        :param LoggerFormat fmt: Format used on the log entries. If set to None
            the logger will be initialized with the value defined on :attr:`FMT_DEFAULT`.
        """
        # Define formatter
        if fmt is None:
            fmt = self.FMT_DEFAULT

        # Create logger (debug level, disabled)
        self._logger = logging.Logger(name=name)
        self._logger.setLevel(level=logging.DEBUG)
        self._logger.disabled = True

        # Set formatter
        fmt = logging.Formatter(fmt=fmt.pattern, style=fmt.style)
        hdlr = logging.StreamHandler()
        hdlr.setFormatter(fmt=fmt)
        self._logger.addHandler(hdlr=hdlr)

    @property
    def logger(self) -> logging.Logger:
        """
        Logger instance.
        """
        return self._logger

    def enable(self) -> None:
        """
        Enables the logger.
        """
        self._logger.disabled = False

    def disable(self) -> None:
        """
        Disables the logger.
        """
        self._logger.disabled = True

    def set_level(self, level: int = logging.DEBUG) -> None:
        """
        Set the logger message level.

        :param int level: Logger level.
        """
        self._logger.setLevel(level=level)
