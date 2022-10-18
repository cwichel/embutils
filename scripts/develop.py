#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Development scripts.

:date:      2022
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

# Built-in
import argparse as ap
import datetime as dt
import importlib.metadata as ilm
import pathlib as pl
import re
import subprocess as sp
import sys
import typing as tp

# External
import toml


# -->> Definitions <<------------------
SCRIPTS_PATH = pl.Path(__file__).parent
"""pl.Path: Scripts path"""
REPOSITORY_PATH = SCRIPTS_PATH.parents[0]
"""pl.Path: Repository ROOT path"""

PROJECT_FILE = REPOSITORY_PATH / "pyproject.toml"
"""pl.Path: Project file path"""
PROJECT_NAME = toml.loads(PROJECT_FILE.open(mode="r").read())["tool"]["poetry"]["name"]
"""str: Project name"""
PROJECT_PATH = REPOSITORY_PATH / PROJECT_NAME
"""pl.Path: Project sources path"""


# -->> Tunables <<---------------------
PROJECT_COV_THS = 90
"""int: Coverage threshold"""

PROJECT_SOURCES = [
    PROJECT_NAME,
    "scripts",
    "tests",
    "docs/conf.py",
]
"""tp.List[str]: List of sources to which run formatters/linters onto"""


# -->> API <<--------------------------
def run_commands(
    cmds: tp.Dict[str, list],
    cwd: pl.Path = REPOSITORY_PATH,
    fail_fast: bool = False,
) -> None:
    """Run several successive commands

    :param tp.Dict[str, list] cmds: Command dictionary with execution arguments
    :param pl.Path cwd:             Commands current working directory.
    :param bool fail_fast:          Flag. If enabled the commands execution will stop on the first fail return
    """
    fail = False
    for key, args in cmds.items():
        print(f"Running {key}...")
        ret = sp.run(args, cwd=cwd)
        if ret.returncode != 0:
            print(f"Process exited with error code {ret.returncode}")
            fail |= True
            if fail_fast:
                sys.exit(ret.returncode)
    sys.exit(1 if fail else 0)


def run_formatter() -> None:
    """Run formatters over the code."""
    # Setup commands
    cmds = {
        "autoflake": ["poetry", "run", "pautoflake", *PROJECT_SOURCES],
        "isort": ["poetry", "run", "isort", *PROJECT_SOURCES],
        "black": ["poetry", "run", "black", *PROJECT_SOURCES],
    }
    # Execute
    run_commands(cmds=cmds, fail_fast=True)


def run_html() -> None:
    """Run a local HTML server to check coverage reports or generated documentation."""
    # Parse arguments
    parser = ap.ArgumentParser()
    parser.add_argument("-c", "--coverage", action="store_true", help="Starts the coverage html server.")
    args = parser.parse_args(args=sys.argv[1:])
    # Run HTML server
    target = "htmlcov" if args.coverage else "docs/_build/html"
    sp.run(["python", "-m", "http.server", "-d", f"{REPOSITORY_PATH / target}"], cwd=REPOSITORY_PATH)


def run_linters() -> None:
    """Run linters and typing checks over the code."""
    # Setup commands
    cmds = {
        "flakeheaven": ["poetry", "run", "flakeheaven", "lint", *PROJECT_SOURCES],
    }
    # Execute
    run_commands(cmds=cmds, fail_fast=True)


def run_tests() -> None:
    """Run tests over the code and check coverage level."""
    # Setup commands
    cmds = {
        "tests": ["poetry", "run", "pytest", "--cov", PROJECT_PATH, "--cov-config", PROJECT_FILE],
        "coverage": ["poetry", "run", "coverage", "report", "--fail-under", str(PROJECT_COV_THS)],
    }
    # Adjust coverage output
    cmds["tests"].extend(["--cov-report", "html:.covhtml"])
    # Execute
    run_commands(cmds=cmds, fail_fast=True)


def run_typing() -> None:
    """Run static typing checks over the code."""
    cmds = {
        "mypy": ["poetry", "run", "mypy"],
    }
    run_commands(cmds=cmds, fail_fast=True)


def update_docs() -> None:
    """Updates and build the documentation for the code"""
    # Update requirements
    with PROJECT_FILE.open(mode="r") as file:
        config = toml.loads(file.read())
        mods = ["toml"]
        mods.extend([req.lower() for req in config["tool"]["poetry"]["dependencies"].keys() if req.lower() != "python"])
        mods.extend([req.lower() for req in config["tool"]["poetry"]["group"]["docs"]["dependencies"].keys()])
    with (REPOSITORY_PATH / "docs/requirements.txt").open(mode="w") as file:
        file.write("\n".join([f"{mod} == {ilm.version(mod)}" for mod in mods]))
    # Execute generation, and build commands
    cmds = {
        "docs generation": ["sphinx-apidoc", "-f", "-P", "-e", "-o", "docs/sources", PROJECT_NAME],
        "docs build": ["sphinx-build", "-b", "html", "-E", "-T", "docs", "docs/_build/html"],
    }
    run_commands(cmds=cmds, fail_fast=True)


def update_version() -> None:
    """Update both poetry and module __init__ version string."""
    ver_str = dt.datetime.now().strftime("%Y.%m.%d").replace(".0", ".")
    # Update poetry version
    sp.run(args=["poetry", "version", ver_str], cwd=REPOSITORY_PATH)
    # Update sources version
    ver_re = re.compile(pattern="^__ver.*", flags=re.I)
    ver_str = f'__version__ = "{ver_str}"'
    ver_file = PROJECT_PATH / "__init__.py"
    with ver_file.open(mode="r") as file:
        lines = file.read().splitlines()
        for idx, line in enumerate(lines):
            if ver_re.search(string=line):
                lines[idx] = ver_str
                break
    with ver_file.open(mode="w") as file:
        file.write("\n".join(lines) + "\n")


# -->> Export <<-----------------------
__all__ = [
    # Methods
    "run_linters",
    "run_formatter",
    "run_html",
    "run_tests",
    "run_typing",
    "update_docs",
    "update_version",
]
"""tp.List[str]: Module available definitions"""
