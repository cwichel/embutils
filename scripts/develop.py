#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Generic development scripts for Poetry-based projects.

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
import pathlib as pl
import subprocess as sp
import sys
import typing as tp


# -->> Tunables <<----------------------
COVERAGE_THRESH: int = 90
"""Coverage threshold for the repository. Analysis below this value will be considered fail."""


# -->> Definitions <<-------------------
CMD_RUN: tp.List[str] = ["poetry", "run"]
"""Base command to run scripts."""

SOURCES: tp.List[str] = [
    "bases",
    "components",
    "development",
    "projects",
    "scripts",
    "test",
]
"""Paths, relative to repository root, that contain project sources"""

REPOSITORY_PATH: pl.Path = pl.Path(__file__).parents[1]
"""Path to the repository root directory."""

PROJECTS_PATH: pl.Path = REPOSITORY_PATH / "projects"
"""Path to the repository projects directory."""

REPOSITORY_CONFIG: pl.Path = REPOSITORY_PATH / "pyproject.toml"
"""Repository configuration file."""

COVERAGE_REPORT: pl.Path = REPOSITORY_PATH / ".covhtml"
"""Coverage report file."""


# -->> Utilities <<---------------------
@dc.dataclass
class Command:
    """Command definition"""

    args: tp.List[str] = dc.field(default_factory=list)
    cwd: pl.Path = dc.field(default=REPOSITORY_PATH)


def execute_commands(
    cmds: tp.Dict[str, Command],
    fail_fast: bool = False,
) -> None:
    """Run several successive commands.

    :param cmds: Commands to run.
    :param fail_fast: Flag. If True, the execution will stop at the first error.
    """
    failed = False
    for key, cmd in cmds.items():
        print(f"Executing {key}...")
        result = sp.run(cmd.args, cwd=cmd.cwd)
        failed |= result.returncode != 0
        if failed:
            errmsg = ((result.stderr or "") + (result.stdout or "")) or "No details available"
            print(f"{key} failed with code {result.returncode}: {errmsg}")
            if fail_fast:
                sys.exit(result.returncode)
    sys.exit(1 if failed else 0)


# -->> Scripts <<-----------------------
def builder(
    # No args
) -> None:
    """Build all projects in the repository."""
    cmds = {}
    for target in PROJECTS_PATH.iterdir():
        if not target.is_dir():
            continue
        cmds[f"build_{target.stem}"] = Command(
            args=["poetry", "build-project"],
            cwd=target,
        )
    execute_commands(
        cmds=cmds,
        fail_fast=False,
    )


def formatters(
    # No args
) -> None:
    """Run formatters over the codebase."""
    cmds = {
        "autoflake": Command(
            args=[*CMD_RUN, "pautoflake", *SOURCES],
        ),
        "isort": Command(
            args=[*CMD_RUN, "isort", *SOURCES],
        ),
        "black": Command(
            args=[*CMD_RUN, "black", *SOURCES],
        ),
    }
    execute_commands(
        cmds=cmds,
        fail_fast=True,
    )


def linters(
    # No args
) -> None:
    """Run linters over the codebase."""
    cmds = {
        "flakeheaven": Command(
            args=[*CMD_RUN, "flakeheaven", "lint", *SOURCES],
        ),
    }
    execute_commands(
        cmds=cmds,
        fail_fast=True,
    )


def tests(
    # No args
) -> None:
    """Run tests over the codebase and prepare a coverage report/validation."""
    cmds = {
        "tests": Command(
            args=[
                *CMD_RUN,
                "pytest",
                "--cov",
                REPOSITORY_PATH,
                "--cov-config",
                REPOSITORY_CONFIG,
                "--cov-report",
                f"html:{COVERAGE_REPORT}",
            ],
        ),
        "coverage": Command(
            args=[*CMD_RUN, "coverage", "report", "--fail-under", str(COVERAGE_THRESH)],
        ),
    }
    execute_commands(
        cmds=cmds,
        fail_fast=True,
    )


def tests_report(
    # No args
) -> None:
    """Start a webserver to view the test reports."""
    cmds = {
        "http": Command(
            args=[*CMD_RUN, "python", "-m", "http.server", "-d", 8000, COVERAGE_REPORT],
        ),
    }
    execute_commands(
        cmds=cmds,
        fail_fast=True,
    )


def type_checks(
    # No args
) -> None:
    """Run static typing checks over the codebase."""
    cmds = {
        "mypy": Command(
            args=[*CMD_RUN, "mypy"],
        ),
    }
    execute_commands(
        cmds=cmds,
        fail_fast=True,
    )


# -->> Export <<------------------------
# This is not a package. No code will be exported.


# -->> Execute <<----------------------
# Used as script source by poetry. No code will be executed directly.
if __name__ == "__main__":
    # Use for debug ONLY!
    # build_targets()
    pass
