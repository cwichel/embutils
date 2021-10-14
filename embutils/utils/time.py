#!/usr/bin/python
# -*- coding: ascii -*-
"""
Timing utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from functools import wraps
from time import time
from typing import Callable, TypeVar

from .logger import SDK_LOG


# -->> Definitions <<------------------
RT = TypeVar('RT')


# -->> API <<--------------------------
def timer(name: str = None, log: bool = False, precision: int = 6) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """
    Decorator.
    Used to log the execution time of a function.

    :param str name: Timer name. Used to identify the measurement.
    :param bool log: If true, this info will be captured on the system log. Prints on console otherwise.
    :param float precision: Number of decimals included on elapsed time.

    :return: Decorated function wrapped on timer.
    :rtype: Callable[[Callable[..., RT]], Callable[..., RT]]
    """
    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> RT:
            logger = SDK_LOG.info if log else print
            logger(f"{name}: Starting execution...")
            start = time()
            rv = func(*args, **kwargs)
            total = elapsed(start)
            logger(f"{name}: Execution time: {total:.{precision}f}[s]")
            return rv
        return wrapper
    return decorator


def elapsed(start: float) -> float:
    """
    Computes the elapsed time since the given timestamp.

    :param float start: Start timestamp.

    :returns: Time elapsed.
    :rtype: float
    """
    return time() - start
