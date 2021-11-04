#!/usr/bin/python
# -*- coding: ascii -*-
"""
Service implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import abc
import threading as th
import time
import typing as tp

from .logger import SDK_LOG
from .threading import SDK_TP, SimpleThreadTask


# -->> Definitions <<------------------
#: CallBack definition. None -> None
CBNone2None = tp.Callable[[], None]


# -->> API <<--------------------------
class AbstractService(abc.ABC):
    """
    Service definition abstraction.
    Use this class to simplify the service definition and handling.
    """
    #: Task execution delay.
    TASK_DELAY_S = 0.001

    def __init__(self, delay: float = TASK_DELAY_S) -> None:
        """
        Class initialization.

        :param float delay:     Time between service task executions.
        """
        # Configure service operation
        self._delay     = delay
        self._alive     = True
        self._resumed   = False
        self._ended     = th.Event()        # Set when the service gets terminated.
        self._running   = th.Event()        # Set when the service is running.
        self._executed  = th.Event()        # Set after every main task execution.
        # Start
        self._running.set()
        SDK_TP.enqueue(task=SimpleThreadTask(
            name=f"{self.__class__.__name__}",
            task=self._service
            ))

    def __del__(self):
        """
        Class destructor.
        Ensures to stop the service correctly on deletion.
        """
        self.stop()
        self.join()

    @property
    def is_alive(self) -> bool:
        """
        Returns if the service is alive.
        """
        return self._alive

    @property
    def is_running(self) -> bool:
        """
        Returns if the service is running.
        """
        return self._alive and self._running.is_set()

    @property
    def delay(self) -> float:
        """
        Service main task execution delay in seconds.
        """
        return self._delay

    @delay.setter
    def delay(self, value: float) -> None:
        """
        Service main task execution delay setter.

        :param float value: Delay in seconds.
        """
        self._delay = value

    def resume(self) -> None:
        """
        Resumes the service execution.
        """
        if not self._running.is_set():
            self._resumed = True
            self._running.set()
            SDK_LOG.info(f"{self.__class__.__name__} resumed")

    def pause(self) -> None:
        """
        Pauses the service execution.
        """
        if self._running.is_set():
            self._executed.wait()
            self._running.clear()
            self._on_pause()
            SDK_LOG.info(f"{self.__class__.__name__} paused")

    def stop(self) -> None:
        """
        Stops the service execution.
        """
        self._alive   = False
        self._resumed = False
        self._running.set()

    def join(self) -> None:
        """
        Wait until service is fully terminated.
        """
        self._ended.wait()

    def _service(self) -> None:
        """
        Service process execution.

        #. Runs the starting code.
        #. Run the execution loop until the service stop is requested.
        #. Runs the ending code and return.
        """
        # Start service execution
        SDK_LOG.info(f"{self.__class__.__name__} started")
        self._on_start()
        # Execution loop
        while self._alive:
            # Handle pause / resume
            self._running.wait()
            if self._resumed:
                self._on_resume()
                self._resumed = False
            # Handle termination
            if not self._alive:
                break
            # Run main task
            try:
                self._executed.clear()
                self._task()
            finally:
                self._executed.set()
                time.sleep(self._delay)
        # Run service ending code
        self._on_end()
        self._ended.set()
        SDK_LOG.info(f"{self.__class__.__name__} ended")

    @abc.abstractmethod
    def _task(self) -> None:
        """
        Service core task/logic.
        """

    def _on_start(self) -> None:
        """
        Optional. Called on service start.
        """

    def _on_resume(self) -> None:
        """
        Optional. Called on service resume.
        """

    def _on_pause(self) -> None:
        """
        Optional. Called on service pause.
        """

    def _on_end(self) -> None:
        """
        Optional. Called upon service termination.
        """
