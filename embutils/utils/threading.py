#!/usr/bin/python
# -*- coding: ascii -*-
"""
SDK threading utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from threading import Lock, Thread
from typing import List, Union
from functools import wraps


def synchronous(lock_name: str) -> callable:
    """
    Decorator that can be used in a class to wrap a function or action with a
    lock.

    :param str lock_name: Name of the lock attribute.

    :returns: Callable with the lock wrapped function.
    :rtype: callable
    """
    def _wrapper(func: callable) -> callable:
        """
        Wraps the decorated function to apply the lock.
        """
        @wraps(func)
        def _synchronizer(self, *args, **kwargs):
            """
            Applies the lock over the given function.
            """
            _lock = self.__getattribute__(lock_name)
            with _lock:
                return func(self, *args, **kwargs)
        return _synchronizer
    return _wrapper


class ThreadPool(object):
    """
    Thread pool implementation for ThreadItem instances.

    .. note::
        * This class is implemented as a singleton.
    """

    __inst: Union[None, 'ThreadPool'] = None
    __init: bool = False

    def __new__(cls) -> 'ThreadPool':
        """
        Creates the singleton instance.

        :returns: singleton.
        :rtype: ThreadPool
        """
        if cls.__inst is None:
            cls.__inst = super(ThreadPool, cls).__new__(cls)
            cls.__init = False
        return cls.__inst

    def __init__(self) -> None:
        """
        This class don't require any input from the user to be initialized.
        """
        # Only do this once
        if self.__init:
            return
        self.__init = True

        # Initialize
        self._lock:     Lock = Lock()
        self._threads:  List[Thread] = []

    @property
    @synchronous(lock_name='_lock')
    def count(self) -> int:
        """
        Number of threads registered in the pool.

        :returns: Thread count.
        :rtype: int
        """
        return len(self._threads)

    @property
    @synchronous(lock_name='_lock')
    def active(self) -> int:
        """
        Number of active threads in the pool.

        :returns: Active thread count.
        :rtype: int
        """
        return sum([1 if t.is_alive() else 0 for t in self._threads])

    @synchronous(lock_name='_lock')
    def add(self, thread: Thread) -> None:
        """
        Add a thread to the pool.

        :param Thread thread: Thread to be added into the pool.
        """
        self._threads.append(thread)

    @synchronous(lock_name='_lock')
    def remove(self, thread: Thread) -> None:
        """
        Remove a thread from the pool (if available).

        :param Thread thread: Thread to be removed from the pool.
        """
        if thread in self._threads:
            idx = self._threads.index(thread)
            self._threads.pop(idx)


class ThreadItem(Thread):
    """
    Thread item implementation. All the threads created using this class (daemons
    or not) can be monitored using the ThreadPool class.
    """
    def __init__(self, name: str = 'Unnamed', daemon: bool = True, auto_remove: bool = True, *args, **kwargs) -> None:
        """
        Class initialization.

        :param str name:            Thread name. This name is used to identify the thread on the pool.
        :param bool daemon:         If true the thread will be initialized as daemon.
        :param bool auto_remove:    If true the thread will be deleted after completion.
        """
        # Create thread
        super(ThreadItem, self).__init__(name=name, *args, **kwargs)
        self._auto_remove = auto_remove
        self.setDaemon(daemon)

        # Add thread to pool and start
        ThreadPool().add(thread=self)
        self.start()

    def __del__(self) -> None:
        """
        Class destructor. This method ensures that the thread is removed from the
        pool when deleted.
        """
        ThreadPool().remove(thread=self)

    def run(self) -> None:
        """
        Runs the thread target process. If auto remove is set to true this method
        will attempt to delete the thread when the process finishes the execution.
        """
        super().run()
        if self._auto_remove:
            self.remove()

    def remove(self):
        """
        Removes the thread item from the pool and attempts to delete itself.
        """
        ThreadPool().remove(thread=self)
        del self
