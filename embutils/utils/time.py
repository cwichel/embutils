#!/usr/bin/python
# -*- coding: ascii -*-
"""
Timing utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import functools as fc
import time
import typing as tp

from .logger import SDK_LOG


# -->> Definitions <<------------------
#: TyPe definition. Any value.
TPAny      = tp.TypeVar('TPAny')
#: CallBack definition. Any -> Any
CBAny2Any  = tp.Callable[..., TPAny]


# -->> API <<--------------------------
def timer(name: str = None, log: bool = False, precision: int = 6) -> tp.Callable[[CBAny2Any], CBAny2Any]:
    """
    Decorator.
    Used to log the execution time of a function.

    :param str name: Timer name. Used to identify the measurement.
    :param bool log: If true, this info will be captured on the system log. Prints on console otherwise.
    :param float precision: Number of decimals included on elapsed time.

    :return: Decorated function wrapped on timer.
    :rtype: Callable[[Callable[..., RT]], Callable[..., RT]]
    """
    def decorator(func: CBAny2Any) -> CBAny2Any:
        @fc.wraps(func)
        def wrapper(*args, **kwargs) -> TPAny:
            logger = SDK_LOG.info if log else print
            logger(f"{name}: Starting execution...")
            start = time.time()
            ret = func(*args, **kwargs)
            total = elapsed(start)
            logger(f"{name}: Execution time: {total:.{precision}f}[s]")
            return ret
        return wrapper
    return decorator


def elapsed(start: float) -> float:
    """
    Computes the elapsed time since the given timestamp.

    :param float start: Start timestamp.

    :returns: Time elapsed.
    :rtype: float
    """
    return time.time() - start
