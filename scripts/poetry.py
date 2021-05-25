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
import sys
import subprocess as sp
import toml


VER_OPT = ['patch', 'minor', 'major', 'prepatch', 'preminor', 'premajor', 'prerelease']


def poetry_test() -> None:
    """This script run all the project tests.
    """
    # Run pytest on repo
    sp.call("pytest", shell=True)


def poetry_version() -> None:
    """This script update the toml and init file version strings.
    """
    # Get input
    parser = ap.ArgumentParser()
    parser.add_argument('version', type=str)
    args = parser.parse_args(args=sys.argv[1:])

    # Update version
    _poetry_update_version(ver=args.version)


def _poetry_update_version(ver: str) -> None:
    # Execute poetry version command
    ret = sp.run('poetry version {input}'.format(input=ver), shell=True)
    if ret.returncode != 0:
        raise ValueError(ret.stderr)

    # Parse project name and new version
    with open(file="pyproject.toml", mode="r") as f:
        conf = toml.loads(f.read())
        file = '{name}/__init__.py'.format(name=conf['tool']['poetry']['name'])
        ver = '__version__ = \'{ver}\''.format(ver=conf['tool']['poetry']['version'])

    # Update init file with version
    with open(file=file, mode='r+') as f:
        lines = f.read().split('\n')
        lines = [line if ('__version__' not in line) else ver for line in lines]
        f.seek(0)
        f.write('\n'.join(lines))
