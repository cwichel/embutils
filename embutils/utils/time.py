#!/usr/bin/python
# -*- coding: ascii -*-
"""
Time utilities.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

import time


def time_elapsed(start: float) -> float:
    """Return the time elapsed since start.

    Args:
        start (float): Start timestamp.

    Returns:
        float: Time elapsed.
    """
    return time.time() - start
