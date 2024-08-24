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
                "EMBUTILS_LOGGER_DUMP": str(int(True)),
                "EMBUTILS_LOGGER_FILE": "test.log",
            }
        )
        settings = LoggerSettings()
        # Validate settings against environment variables
        self.assertEqual(settings.name, os.environ["EMBUTILS_LOGGER_NAME"])
        self.assertEqual(settings.level, int(os.environ["EMBUTILS_LOGGER_LEVEL"]))
        self.assertEqual(settings.dump, bool(int(os.environ["EMBUTILS_LOGGER_DUMP"])))
        self.assertEqual(settings.file, pl.Path(os.environ["EMBUTILS_LOGGER_FILE"]))
        # Cleanup
        if settings.file.exists():
            settings.file.unlink()

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
                    "EMBUTILS_LOGGER_FILE": "test.log",
                    "EMBUTILS_LOGGER_DUMP": str(int(True)),
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
            file = pl.Path(os.environ["EMBUTILS_LOGGER_FILE"])
            shutdown_logger(logger=logger, file_only=True)
            # Validate and cleanup
            with file.open("r") as f:
                self.assertEqual(len(f.readlines()), count)
            if file.exists():
                file.unlink()


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
