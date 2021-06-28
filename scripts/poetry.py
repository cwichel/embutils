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
import subprocess as sp
import toml
from pathlib import Path

#: Project root path
ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parent

#: Project poetry file
PRJ_TOML = ROOT / 'pyproject.toml'

#: Project name
PRJ_NAME = toml.loads(open(file=PRJ_TOML, mode='r').read())['tool']['poetry']['name']

#: Project path
PRJ_PATH = ROOT / PRJ_NAME

#: Version modifier options
VER_OPT = ['minor', 'major', 'patch', 'post', 'prepatch', 'preminor', 'premajor', 'prerelease']


def run_test() -> None:
    """
    Run the project tests.
    """
    # Run pytest on repo
    sp.call('pytest', shell=True)


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
    path = ROOT / 'docs'

    # Generate code documentation
    if args.generate:
        # Define paths
        out = path / '_source'
        # Remove old
        if out.exists():
            shutil.rmtree(path=out)
        out.mkdir()
        # Generate new
        cmd = f'sphinx-apidoc -f -P -e -o "{out}" "{PRJ_PATH}"'
        sp.call(cmd, shell=True)

    # Clean las code build
    if args.clean:
        cmd = f'{path / "make"} clean'
        sp.call(cmd, shell=True)

    # Build new documentation
    if args.build:
        out = path / '_build/html'
        cmd = f'sphinx-build -b html -E -T "{path}" "{out}"'
        sp.call(cmd, shell=True)


def run_html() -> None:
    """
    Enables a HTML server to render/check the generated documentation.
    """
    docs_base_path = ROOT / 'docs'
    docs_html_path = docs_base_path / '_build/html'

    # Run the documentation make
    cmd = f'python -m http.server -d "{docs_html_path}"'
    sp.call(cmd, shell=True)


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
        with open(file=PRJ_TOML, mode="r") as f:
            conf = toml.loads(f.read())
            tmp  = conf['tool']['poetry']['version'].split('.')
            tmp[-1] = f'post{tmp[-1]}'
            ver  = '.'.join(tmp)

    # Execute poetry version command
    ret = sp.run(f'poetry version {ver}', shell=True)
    if ret.returncode != 0:
        raise ValueError(ret.stderr)

    # Parse project name and new version
    with open(file=PRJ_TOML, mode="r") as f:
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
