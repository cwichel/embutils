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

from .common import TPAny, CBAny2Any


# -->> Definitions <<------------------


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
            tim = Timer()
            ret = func(*args, **kwargs)
            tot = tim.elapsed()
            if logger is not None:
                logger(f"{name}: Execution time: {tot:.{precision}f}[s]")
            return ret
        return wrapper
    return decorator


class Timer:
    """
    Simple process timer.
    """
    def __init__(self) -> None:
        """
        This class don't require any input from the user to be initialized.
        """
        self._start = 0.0
        self.start()

    def start(self) -> float:
        """
        Updates the timer start timestamp.

        :returns: Start time.
        :rtype: float
        """
        self._start = time.perf_counter()
        return self._start

    def elapsed(self, update: bool = False) -> float:
        """
        Computes the time elapsed since the latest timer start.

        :param bool update: Computes elapsed time and updated the start time.

        :returns: Time elapsed.
        :rtype: float
        """
        now = time.perf_counter()
        ret = now - self._start
        if update:
            self._start = now
        return ret
