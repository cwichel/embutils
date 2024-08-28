#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""System logger utility.

:date:      2024
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# --------------------------------------
__author__ = "Christian Wiche"
__version__ = "ALPHA"
# --------------------------------------

# Built-in
import dataclasses as dc
import datetime as dt
import functools as ft
import logging as log
import logging.config as log_c
import os
import pathlib as pl
import typing as tp


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
@dc.dataclass
class LoggerSettings:
    """System logger settings.

    :param name: Logger name.
    :param level: Logger level.
    :param use_file: Enable log dump.
    """

    name: str = dc.field(default_factory=ft.partial(os.environ.get, "EMBUTILS_LOGGER_NAME", "EMBUTILS"))
    level: int = dc.field(default_factory=ft.partial(os.environ.get, "EMBUTILS_LOGGER_LEVEL", log.DEBUG))
    use_file: bool = dc.field(default_factory=ft.partial(os.environ.get, "EMBUTILS_LOGGER_USE_FILE", False))
    file: pl.Path = dc.field(init=False, default=None)

    formatters = {
        "standard": {
            "format": "{asctime} | {name:^8s} | {levelname:^8s} | {module:<20s}: {message:s}",
            "datefmt": "%Y-%m-%d_%H:%M:%S",
            "style": "{",
        },
    }
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": log.DEBUG,
            "stream": "ext://sys.stdout",
        },
    }
    loggers = {}

    def __post_init__(
        self,
    ) -> None:
        """Initialize the logger settings."""
        # Format settings
        self.level = int(self.level)
        self.use_file = bool(int(self.use_file))
        # Configure logger
        self.loggers[self.name] = {
            "level": self.level,
            "handlers": ["console"],
            "propagate": False,
        }
        self.handlers["console"]["level"] = self.level
        # Configure dump file
        if self.use_file:
            self.file = pl.Path.home() / f".logs/{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            self.loggers[self.name]["handlers"].append("file")
            self.handlers["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "level": self.level,
                "filename": str(self.file),
                "mode": "a",
                "maxBytes": 10 * (1024 * 1024),
                "backupCount": 10,
            }
            if not self.file.parent.exists():
                self.file.parent.mkdir(parents=True, exist_ok=True)

    def dict(
        self,
    ) -> dict:
        """Return the logger settings as a dict.

        :return: Logger settings dictionary.
        """
        return {
            "version": 1,
            "formatters": self.formatters,
            "handlers": self.handlers,
            "loggers": self.loggers,
        }


# -->> API <<---------------------------
def create_logger(
    settings: tp.Optional[LoggerSettings] = None,
) -> log.Logger:
    """Create a logger instance.

    :param settings: Logger settings.

    :return: Logger instance.
    """
    if settings is None:
        settings = LoggerSettings()
    log_c.dictConfig(settings.dict())
    return log.getLogger(settings.name)


def shutdown_logger(
    logger: log.Logger,
    file_only: bool = False,
) -> None:
    """Close a logger instance.

    :param logger: Logger instance.
    :param file_only: Close only the file handler.
    """
    # Full shutdown
    if not file_only:
        log.shutdown()
        return
    # File only
    for handler in logger.handlers:
        if isinstance(handler, log.FileHandler):
            handler.close()


# -->> Export <<------------------------
__all__ = [
    "LoggerSettings",
    "create_logger",
    "shutdown_logger",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
