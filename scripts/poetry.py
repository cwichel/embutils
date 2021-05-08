#!/usr/bin/python
# -*- coding: ascii -*-
"""
Poetry scripts.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""
import subprocess as sp


def poetry_test() -> None:
    """This script run all the project tests.
    """
    # Run pytest on repo
    sp.call("pytest", shell=True)
