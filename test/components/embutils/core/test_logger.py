#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""System logger utility test suite.

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
import logging as log
import os
import pathlib as pl
import unittest as ut

# External
from embutils.core import LoggerSettings, create_logger, shutdown_logger


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class LoggerTestSuite(ut.TestCase):
    def test_settings(
        self,
    ) -> None:
        """Test logger configuration."""
        # Create logger settings
        os.environ.update(
            {
                "EMBUTILS_LOGGER_NAME": "TEST",
                "EMBUTILS_LOGGER_LEVEL": str(log.DEBUG),
                "EMBUTILS_LOGGER_USE_FILE": str(int(True)),
            }
        )
        settings = LoggerSettings()
        # Validate settings against environment variables
        self.assertEqual(settings.name, os.environ["EMBUTILS_LOGGER_NAME"])
        self.assertEqual(settings.level, int(os.environ["EMBUTILS_LOGGER_LEVEL"]))
        self.assertEqual(settings.use_file, bool(int(os.environ["EMBUTILS_LOGGER_USE_FILE"])))
        # Cleanup
        logfile = settings.file
        if logfile.exists():
            logfile.unlink()
        if not list(logfile.parent.iterdir()):
            logfile.parent.rmdir()

    def test_fileDump(
        self,
    ) -> None:
        """Validate log dumps and levels."""
        pair = [
            [log.DEBUG, 5],
            [log.INFO, 4],
            [log.WARNING, 3],
        ]
        for level, count in pair:
            # Create logger
            os.environ.update(
                {
                    "EMBUTILS_LOGGER_LEVEL": str(level),
                    "EMBUTILS_LOGGER_USE_FILE": str(int(True)),
                }
            )
            logger = create_logger()
            # Generate log messages
            logger.debug("This is a debug message.")
            logger.info("This is an info message.")
            logger.warning("This is a warning message.")
            logger.error("This is an error message.")
            logger.critical("This is a critical message.")
            # Close log
            shutdown_logger(logger=logger)
            # Validate and cleanup
            logfiles = [logfile for logfile in logger.handlers if isinstance(logfile, log.FileHandler)]
            for logfile in logfiles:
                item = pl.Path(logfile.baseFilename)
                with item.open(mode="r") as file:
                    self.assertEqual(len(file.readlines()), count)
                if item.exists():
                    item.unlink()
                if not list(item.parent.iterdir()):
                    item.parent.rmdir()


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
