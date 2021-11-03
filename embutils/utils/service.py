#!/usr/bin/python
# -*- coding: ascii -*-
"""
Service implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import threading as th
import typing as tp

from .logger import SDK_LOG, Logger
from .threading import SDK_TP, ThreadPool, SimpleThreadTask


# -->> Definitions <<------------------
#: CallBack definition. None -> None
CBNone2None = tp.Callable[[], None]


# -->> API <<--------------------------
class Service:
    """
    Service implementation.
    This class simplifies the services definition and handling for the SDK. 
    """
    def __init__(self,
                 task: CBNone2None, start: CBNone2None = None, end: CBNone2None = None,
                 pool: ThreadPool = SDK_TP, logger: Logger = SDK_LOG) -> None:
        """
        Class initialization.

        :param CBNone2None task:    Service main task callback.
        :param CBNone2None start:   Service start callback.
        :param CBNone2None end:     Service ending callback.
        :param ThreadPool pool:     Thread pool to be used by the service.
        :param Logger logger:       Logger to be used by the service.
        """
        # Function to handle empty callbacks
        def do_nothing(): pass

        # System related
        self._pool    = pool
        self._logger  = logger
        # Configure execution callbacks
        self._task    = task
        self._start   = start if (end is not None) else do_nothing()
        self._end     = end if (end is not None) else do_nothing()
        # Configure service operation
        self._alive   = th.Event()
        self._ended   = th.Event()
        self._working = th.Event()
        self._running = th.Event()
        # Start
        self._alive.set()
        self._running.set()
        self._pool.enqueue(task=SimpleThreadTask(
            name=f"{self.__class__.__name__}.service",
            task=self._process
            ))

    def __del__(self):
        """
        Ensures to stop the service correctly on deletion.
        """
        self.stop()
        self.join()

    @property
    def is_alive(self) -> bool:
        """
        Returns if the service is alive.
        """
        return self._alive.is_set()

    @property
    def is_running(self) -> bool:
        """
        Returns if the service is running.
        """
        return self._alive.is_set() and self._running.is_set()

    def resume(self) -> None:
        """
        Resumes the service execution.
        """
        self._running.set()

    def pause(self) -> None:
        """
        Pauses the service loop and waits until the internal task is finished.
        """
        self._running.clear()
        self._working.wait()

    def stop(self) -> None:
        """
        Ask the service to stop its execution.
        """
        self._alive.clear()

    def join(self) -> None:
        """
        Wait until service is fully terminated.
        """
        self._ended.wait()

    def _process(self) -> None:
        """
        Service process execution.

        #. Runs the starting code.
        #. Run the execution loop until the service stop is requested.
        #. Runs the ending code and return.
        """
        # Start service execution
        self._logger.info(f"{self.__class__.__name__}.service started")
        self._ended.clear()
        self._start()

        # Execution loop
        while self._alive.is_set():
            self._running.wait()
            try:
                self._working.clear()
                self._task()
            finally:
                self._working.set()

        # Run service ending code
        self._end()
        self._ended.set()
        self._logger.info(f"{self.__class__.__name__}.service ended")
