#!/usr/bin/python
# -*- coding: ascii -*-
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

from pathlib import Path

from embutils.repo import execute


# -->> Definitions <<----------------------------------------------------------
# Base Paths
#: Script path
PATH_THIS = Path(os.path.abspath(os.path.dirname(__file__)))
#: Root path
PATH_ROOT = PATH_THIS.parent

# Project Definitions
#: Project poetry file
PROJ_TOML = PATH_ROOT / 'pyproject.toml'
#: Project name
PROJ_NAME = toml.loads(open(file=PROJ_TOML, mode='r').read())['tool']['poetry']['name']
#: Project path
PROJ_PATH = PATH_ROOT / PROJ_NAME

# Script definitions
#: Version modifier options
VER_OPT = ['minor', 'major', 'patch', 'post', 'prepatch', 'preminor', 'premajor', 'prerelease']


# -->> API <<------------------------------------------------------------------
def run_test() -> None:
    """
    Run the project tests.
    """
    path = PATH_ROOT / 'tests'
    cmd = f"pytest {path}"
    execute(cmd=cmd)


def run_docs() -> None:
    """
    Run the documentation build process.
    """
    # Get input
    parser = ap.ArgumentParser()
    parser.add_argument('-b', '--build', action='store_true', help='Build documentation files.')
    parser.add_argument('-c', '--clean', action='store_true', help='Clean generated documentation.')
    parser.add_argument('-g', '--generate', action='store_true', help='Generate code documentation.')
    args = parser.parse_args(args=sys.argv[1:])

    # Define base path
    path = PATH_ROOT / 'docs'

    # Generate code documentation
    if args.generate:
        # Define paths
        out = path / '_source'
        # Remove old
        if out.exists():
            shutil.rmtree(path=out)
        out.mkdir()
        # Generate new
        cmd = f'sphinx-apidoc -f -P -e -o "{out}" "{PROJ_PATH}"'
        execute(cmd=cmd)

    # Clean las code build
    if args.clean:
        cmd = f'{path / "make"} clean'
        execute(cmd=cmd)

    # Build new documentation
    if args.build:
        out = path / '_build/html'
        cmd = f'sphinx-build -b html -E -T "{path}" "{out}"'
        execute(cmd=cmd)


def run_html() -> None:
    """
    Enables a HTML server to render/check the generated documentation.
    """
    path = PATH_ROOT / 'docs/_build/html'
    cmd = f'python -m http.server -d "{path}"'
    execute(cmd=cmd)


def run_coverage() -> None:
    """
    Runs coverage over project tests.
    """
    name = PROJ_NAME
    path = PATH_ROOT / 'tests'
    cmd = f'coverage run -m --source={name} pytest {path} && coverage report'
    execute(cmd=cmd)


def run_linter() -> None:
    """
    Runs linter checks over code.
    """
    parser = ap.ArgumentParser()
    parser.add_argument('-d', '--disable', type=str, default='C0301,W1203', help='Linter messages to disable.')
    parser.add_argument('-j', '--cores', type=int, default=4, help='Cores used for linter.')
    args = parser.parse_args(args=sys.argv[1:])

    name    = PROJ_NAME
    cmd = f'pylint {name} -d "{args.disable}" -j "{args.cores}"'
    execute(cmd=cmd)


def run_version() -> None:
    """
    This script update the toml and init file version strings.
    """
    # Get input
    parser = ap.ArgumentParser()
    parser.add_argument('version', type=str)
    args = parser.parse_args(args=sys.argv[1:])

    # Update version
    _update_version(ver=args.version)


def _update_version(ver: str) -> None:
    """
    Update the version number on the init and toml files.

    :param str ver: Version string. It can be a version string like 1.0.0 or
        any of the options listed in `VER_OPT`.
    """
    # Check if we need to fix the version
    if ver == 'post':
        with open(file=PROJ_TOML, mode="r") as f:
            conf = toml.loads(f.read())
            tmp  = conf['tool']['poetry']['version'].split('.')
            tmp[-1] = f'post{tmp[-1]}'
            ver  = '.'.join(tmp)

    # Execute poetry version command
    ret = execute(f'poetry version {ver}', ret=True)
    if ret.returncode != 0:
        raise ValueError(ret.stderr)

    # Parse project name and new version
    with open(file=PROJ_TOML, mode="r") as f:
        conf = toml.loads(f.read())
        file = f"{conf['tool']['poetry']['name']}/__init__.py"
        ver  = f"__version__ = \'{conf['tool']['poetry']['version']}\'"

    # Read file and generate the new content update
    with open(file=file, mode='r') as f:
        lines = f.read().split('\n')
        lines = [line if ('__version__' not in line) else ver for line in lines]

    # Write contents 
    with open(file=file, mode='w') as f:
        f.write('\n'.join(lines))
