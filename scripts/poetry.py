#!/usr/bin/python
# -*- coding: ascii -*-
"""
Poetry scripts.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

import argparse as ap
import os
import sys
import subprocess as sp
import toml
from pathlib import Path

ROOT    = Path(os.path.dirname(os.path.abspath(__file__))).parent
VER_OPT = ['minor', 'major', 'patch', 'post', 'prepatch', 'preminor', 'premajor', 'prerelease']


def run_test() -> None:
    """This script run all the project tests.
    """
    # Run pytest on repo
    sp.call("pytest", shell=True)


def run_version() -> None:
    """This script update the toml and init file version strings.
    """
    # Get input
    parser = ap.ArgumentParser()
    parser.add_argument('version', type=str)
    args = parser.parse_args(args=sys.argv[1:])

    # Update version
    _update_version(ver=args.version)


def _update_version(ver: str) -> None:
    # Check if we need to fix the version
    if ver == 'post':
        with open(file="pyproject.toml", mode="r") as f:
            conf = toml.loads(f.read())
            tmp  = conf['tool']['poetry']['version'].split('.')
            tmp[-1] = f'post{tmp[-1]}'
            ver  = '.'.join(tmp)

    # Execute poetry version command
    ret = sp.run(f'poetry version {ver}', shell=True)
    if ret.returncode != 0:
        raise ValueError(ret.stderr)

    # Parse project name and new version
    with open(file="pyproject.toml", mode="r") as f:
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
