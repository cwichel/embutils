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


# -->> Definitions <<------------------
#: TyPe definition. Any value.
TPAny      = tp.TypeVar('TPAny')
#: CallBack definition. Any -> Any
CBAny2Any  = tp.Callable[..., TPAny]


# -->> API <<--------------------------
def timer(name: str = None, logger: CBAny2Any = print, precision: int = 6) -> tp.Callable[[CBAny2Any], CBAny2Any]:
    """
    Decorator.
    Used to log the execution time of a function.

    :param str name:            Timer name. Used to identify the measurement.
    :param CBAny2Any logger:    Callable used to print the time logs. By default, system print.
    :param float precision:     Number of decimals included on elapsed time.

    :return: Decorated function wrapped on timer.
    :rtype: Callable[[Callable[..., RT]], Callable[..., RT]]
    """
    def decorator(func: CBAny2Any) -> CBAny2Any:
        @fc.wraps(func)
        def wrapper(*args, **kwargs) -> TPAny:
            start = time.time()
            ret = func(*args, **kwargs)
            total = elapsed(start)
            if logger is not None:
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
