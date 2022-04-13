#!/usr/bin/python
# -*- coding: ascii -*-
"""
Math utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import math


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
def closest_multi(ref: float, base: float, force_next: bool = False) -> float:
    """
    Computes the closest multiple of 'base' based on a given reference.

    :param float ref:       Reference.
    :param float base:      Multiple base.
    :param bool force_next: If reference is equal to multiple, forces next multiple.

    :return: Closest multiple.
    :rtype: float
    """
    mod = ref % base
    if mod != 0:
        return ref + (base - mod)
    return ref + base if force_next else ref


def closest_pow(ref: float, base: float, force_next: bool = False) -> float:
    """
    Computes the closest power of 'base' based on a given reference.

    :param float ref:       Reference
    :param float base:      Exponential base
    :param bool force_next: If reference is equal to power of base, forces next power.

    :return: Closest power.
    :rtype: float
    """
    aux = round(math.log(ref, base))
    val = base ** aux
    if (val < ref) or (force_next and (val == ref)):
        val = base ** (aux + 1)
    return val


# -->> Export <<-----------------------
__all__ = [
    "closest_multi",
    "closest_pow",
    ]
