#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Poetry utility scripts.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import argparse as ap
import os
import shutil
import sys
import toml
import typing as tp

from embutils.utils import ENCODE, Path, execute


# -->> Definitions <<----------------------------------------------------------
# Base paths
#: Script path
PATH_THIS = Path(os.path.abspath(os.path.dirname(__file__)))
#: Root path
PATH_ROOT = PATH_THIS.parent

# Project settings
#: Project poetry file
PROJ_TOML = PATH_ROOT / "pyproject.toml"
#: Project name
PROJ_NAME = toml.loads(open(file=PROJ_TOML, mode="r").read())["tool"]["poetry"]["name"]
#: Project path
PROJ_PATH = PATH_ROOT / PROJ_NAME

# Script definitions
#: Version modifier options
VER_OPT = ["minor", "major", "patch", "post", "prepatch", "preminor", "premajor", "prerelease"]


# -->> API <<------------------------------------------------------------------
def run_docs() -> None:
    """
    Run the documentation build process.
    """
    # Prepare
    path_docs   = PATH_ROOT / "docs"
    path_source = path_docs / "_source"
    path_build  = path_docs / "_build/html"
    docs_make   = path_docs / "make"

    # Update the requirements
    req_file = path_docs / "requirements.txt"
    req_data = _requirements_get(inc_dev=True)
    with req_file.open(mode="w", encoding=ENCODE) as file:
        file.write("\n".join(req_data))

    # Generate documentation sources
    if path_source.exists():
        shutil.rmtree(path=path_source)
    path_source.mkdir()
    execute(cmd=f"sphinx-apidoc -f -P -e -o {path_source} {PROJ_PATH}")

    # Clean old documentation
    execute(cmd=f"{docs_make} clean")

    # Build documentation
    execute(cmd=f"sphinx-build -b html -E -T {path_docs} {path_build}")


def run_html() -> None:
    """
    Enables a HTML server to render/check the generated documentation or coverage report.
    """
    # Parse arguments
    parser = ap.ArgumentParser()
    parser.add_argument("-c", "--coverage", action="store_true", help="Starts the coverage html server.")
    args = parser.parse_args(args=sys.argv[1:])

    # Run HTML server
    target = "htmlcov" if args.coverage else "docs/_build/html"
    execute(cmd=f"python -m http.server -d {PATH_ROOT / target}")


def run_test() -> None:
    """
    Run the project tests.
    """
    path = PATH_ROOT / "tests"
    execute(cmd=f"pytest {path}")


def run_version() -> None:
    """
    This script update the toml and init file version strings.
    """
    # Parse arguments
    parser = ap.ArgumentParser()
    parser.add_argument("version", type=str)
    args = parser.parse_args(args=sys.argv[1:])

    # Run
    _version_update(ver=args.version.lower())


def run_check_coverage() -> None:
    """
    Runs coverage over project tests.
    """
    cmd = f"coverage run -m --source={PROJ_NAME} pytest {PATH_ROOT / 'tests'} && coverage html && coverage report"
    execute(cmd=cmd)


def run_check_linter() -> None:
    """
    Runs linter checks over code.
    """
    parser = ap.ArgumentParser()
    parser.add_argument("-d", "--disable", type=str, default="C0301,W1203", help="Linter messages to disable.")
    parser.add_argument("-j", "--cores", type=int, default=4, help="Cores used to run linter.")
    args = parser.parse_args(args=sys.argv[1:])

    cmd  = f"pylint {PROJ_NAME} -d {args.disable} -j {args.cores}"
    execute(cmd=cmd)


def run_check_types() -> None:
    """
    Runs a type checker over code.
    """
    execute(cmd=f"mypy {PROJ_NAME}")


def _requirements_get(inc_dev: bool = False, inc_extra: str = None) -> tp.List[str]:
    """
    Extract requirements from poetry.

    :param bool inc_dev:    Enable the export of development requirements.
    :param str inc_extra:   Enable the export of one or more extra requirements.

    :return: Requirements list.
    :rtype: tp.List[str]
    """
    # Prepare command
    cmd = "poetry export --without-hashes"
    cmd += " --dev" if inc_dev else ""
    cmd += f" --extras \"{inc_extra}\"" if inc_extra else ""

    # Get requirements
    ret = execute(cmd=cmd, pipe=False)
    if ret.returncode != 0:
        raise ValueError(ret.stderr)

    # Parse and return
    return [line.split(";")[0] for line in ret.stdout.strip().split("\r\n")]


def _version_get() -> str:
    """
    Returns the version string from the poetry project file.

    :return: Version string.
    :rtype: str
    """
    with PROJ_TOML.open(mode="r") as f:
        config = toml.loads(f.read())
        return config["tool"]["poetry"]["version"]


def _version_update(ver: str) -> None:
    """
    Update the version number on the init and toml files.

    :param str ver: Version string. It can be a version string like 1.0.0 or
        any of the options listed in `VER_OPT`.
    """
    # Check if we need to fix the version with post tags
    if ver == "post":
        num = 0
        old = _version_get()
        if "post" in old:
            tmp = old.split(".")
            old = ".".join(tmp[:-1])
            num = int(tmp[-1].replace("post", "")) + 1
        ver = f"{old}.post{num}"

    # Execute poetry version command
    ret = execute(cmd=f"poetry version {ver}")
    if ret.returncode != 0:
        raise ValueError(ret.stderr)

    # Update version on init file
    upd = PROJ_PATH / "__init__.py"
    new = f"__version__ = '{_version_get()}'"
    with upd.open(mode="r") as file:
        lines = file.read().split("\n")
        lines = [(line if ("__version__" not in line) else new) for line in lines]
    with upd.open(mode="w") as file:
        file.write("\n".join(lines))
