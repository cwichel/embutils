#!/usr/bin/env python
##
# @file       singleton.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Singleton implementation.
# =============================================================================


class Singleton(object):
    """Singleton pattern.
    """
    __inst = None
    __init = False

    def __new__(cls, *args, **kwargs) -> 'Singleton':
        """Singleton creation.
        Only create the instance once.
        """
        if cls.__inst is None:
            cls.__inst = super(Singleton, cls).__new__(cls)
            cls.__init = False
        return cls.__inst

    def __init__(self) -> None:
        """Class initialization.
        """
        if self.__init:
            return
        self.__init = True
