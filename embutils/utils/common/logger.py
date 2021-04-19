#!/usr/bin/python
# -*- coding: ascii -*-
"""
SDK logger.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

import logging
from dataclasses import dataclass


@dataclass
class LoggerFormat:
    """Class used to contain a logger format configuration.

    By default:
    """
    pattern:    str = '{created:.05f}: {name:<8s}: {levelname:<8s}: {module:<20s}: {message:s}'
    style:      str = '{'


class Logger:
    """Implement a basic logger handler class.
    """
    FMT_BASE = LoggerFormat()

    def __init__(self, name: str = '', fmt: LoggerFormat = None) -> None:
        """Class initialization. Apply a basic configuration to the logger.

        Args:
            name (str): Logger name.
            fmt (LoggerFormat): Log entries format.
        """
        # Define formatter
        if fmt is None:
            fmt = self.FMT_BASE

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
        """Get the logger handler.

        Return:
            logging.Logger: Logger handler.
        """
        return self._logger

    def enable(self) -> None:
        """Enable the logger.
        """
        self._logger.disabled = False

    def disable(self) -> None:
        """Disable the logger.
        """
        self._logger.disabled = True

    def set_level(self, level: int = logging.DEBUG) -> None:
        """Set the logger messages level.

        Args:
            level (int): Logger level.
        """
        self._logger.setLevel(level=level)


# Create a logger for internal use
LOG_SDK = Logger(name='EMBUTILS')
