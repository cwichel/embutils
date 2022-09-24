#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Repository development tasks and utilities.

:date:      2022
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

# Built-in
import datetime as dt
import importlib.metadata as ilm
import pathlib as pl
import re
import sys
import typing as tp

# External
import invoke as inv
import toml

# Project
import embutils.utils as embu


# -->> Definitions <<------------------
REPOSITORY_PATH = pl.Path(__file__).parent
"""pl.Path: Repository ROOT path"""
PROJECT_FILE = REPOSITORY_PATH / "pyproject.toml"
"""pl.Path: Project file"""
PROJECT_NAME = toml.loads(PROJECT_FILE.open(mode="r").read())["tool"]["poetry"]["name"]
"""str: Project name"""


# -->> Tunables <<---------------------
COVERAGE_THRESHOLD = 90
"""int: Coverage failure threshold"""
SOURCES = [
    PROJECT_NAME,
    "tests",
    "docs/conf.py",
    "tasks.py",
]
"""tp.List[str]: List of sources to which run formatters/linters onto"""


# -->> API <<--------------------------
def run_commands(
    cmds: tp.Dict[str, list],
    fail_fast: bool = False,
) -> None:
    """Run several successive commands"""
    fail = False
    for key, args in cmds.items():
        print(f"Running {key}...")
        ret = embu.execute(args=args, cwd=REPOSITORY_PATH)
        if ret.returncode != 0:
            print(f"Process exited with error code {ret.returncode}")
            fail |= True
            if fail_fast:
                sys.exit(ret.returncode)
    sys.exit(1 if fail else 0)


# -->> Tasks <<------------------------
@inv.task
def run_formatter(context):
    """Run formatters over the code."""
    # Setup commands
    cmds = {
        "autoflake": ["poetry", "run", "pautoflake", *SOURCES],
        "isort": ["poetry", "run", "isort", *SOURCES],
        "black": ["poetry", "run", "black", *SOURCES],
    }
    # Execute
    run_commands(cmds=cmds, fail_fast=True)


@inv.task
def run_linter(context):
    """Run linter and typing checks over the code."""
    # Setup commands
    cmds = {
        "flakeheaven": ["poetry", "run", "flakeheaven", "lint", *SOURCES],
    }
    # Execute
    run_commands(cmds=cmds, fail_fast=True)


@inv.task
def run_tests(contex):
    """Run the repository code tests and compute coverage."""
    # Setup commands
    cmds = {
        "tests": ["poetry", "run", "pytest", "--cov", PROJECT_NAME, "--cov-config", PROJECT_FILE],
        "coverage": ["poetry", "run", "coverage", "report", "--fail-under", str(COVERAGE_THRESHOLD)],
    }
    # Adjust coverage output
    cmds["tests"].extend(["--cov-report", "html:.covhtml"])
    # Execute
    run_commands(cmds=cmds, fail_fast=True)


@inv.task
def run_typing(context):
    """Perform typing checks. This might not be required fos commit/publish."""
    cmds = {
        "mypy": ["poetry", "run", "mypy"],
    }
    run_commands(cmds=cmds, fail_fast=True)


@inv.task
def start_html_coverage(context):
    """Starts an HTML service to review the coverage reports."""
    try:
        docs = embu.validate_dir(path=REPOSITORY_PATH / ".covhtml", must_exist=True)
        embu.execute(args=["python", "-m", "http.server", "-d", docs], cwd=REPOSITORY_PATH)
    except (FileNotFoundError, FileExistsError) as ex:
        print(ex)


@inv.task
def start_html_documentation(context):
    """Starts an HTML service to browse the compiled documentation."""
    try:
        docs = embu.validate_dir(path=REPOSITORY_PATH / "docs/_build/html", must_exist=True)
        embu.execute(args=["python", "-m", "http.server", "-d", docs], cwd=REPOSITORY_PATH)
    except (FileNotFoundError, FileExistsError) as ex:
        print(ex)


@inv.task
def update_documentation(context):
    """Update and build the module documentation."""
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


@inv.task
def update_version(context):
    """Update both poetry and module __init__ version string."""
    ver_str = dt.datetime.now().strftime("%Y.%m.%d").replace(".0", ".")
    # Update poetry version
    embu.execute(args=["poetry", "version", ver_str], cwd=REPOSITORY_PATH)
    # Update sources version
    ver_re = re.compile(pattern="^__ver.*", flags=re.I)
    ver_str = f'__version__ = "{ver_str}"'
    ver_file = REPOSITORY_PATH / f"{PROJECT_NAME}/__init__.py"
    with ver_file.open(mode="r") as file:
        lines = file.read().splitlines()
        for idx, line in enumerate(lines):
            if ver_re.search(string=line):
                lines[idx] = ver_str
                break
    with ver_file.open(mode="w") as file:
        file.write("\n".join(lines) + "\n")


# -->> Invoke Namespace <<-------------
inv_ns = inv.Collection(
    run_formatter,
    run_linter,
    run_tests,
    start_html_coverage,
    start_html_documentation,
    update_documentation,
    update_version,
)
"""inv.Collection: User exposed tasks"""
