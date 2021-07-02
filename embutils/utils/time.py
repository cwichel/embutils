#!/usr/bin/python
# -*- coding: ascii -*-
"""
Time utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import time


def time_elapsed(start: float) -> float:
    """
    Computes the elapsed time since the given timestamp.

    :param float start: Start timestamp.

    :returns: Time elapsed.
    :rtype: float
    """
    return time.time() - start
