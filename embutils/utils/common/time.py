#!/usr/bin/env python
##
# @file       time.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Time related functionalities.
# =============================================================================

import time


def time_elapsed(start: float) -> float:
    """Return the time elapsed since start.

    Args:
        start (float): Start timestamp.

    Returns:
        float: Time elapsed.
    """
    return time.time() - start
