#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Threading utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import abc
import functools as fc
import queue
import threading as th
import typing as tp

from .common import TPAny, CBAny2Any, CBAny2None
from .logger import SDK_LOG


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
def sync(lock_name: str) -> tp.Callable[[CBAny2Any], CBAny2Any]:
    """
    Decorator.
    Used to wrap a class method with a given lock attribute.

    :param str lock_name: Lock attribute name.

    :returns: Decorated function wrapped on the given lock.
    :rtype: Callable[[Callable[..., RT]], Callable[..., RT]]
    """
    def decorator(func: CBAny2Any) -> CBAny2Any:
        @fc.wraps(func)
        def wrapper(self, *args, **kwargs) -> TPAny:
            lock = self.__getattribute__(lock_name)
            with lock:
                return func(self, *args, **kwargs)
        return wrapper
    return decorator


def get_threads(name: str = None, alive: bool = False) -> tp.List[th.Thread]:
    """
    Return all the live threads.

    :param str name:    Filter. If provided, return threads that have or contain this name.
    :param bool alive:  Filter. If enabled, return alive threads only.

    :returns: List with named threads.
    :rtype: list
    """
    threads = th.enumerate()
    if alive:
        threads = [thread for thread in threads if thread.is_alive()]
    if name is not None:
        threads = [thread for thread in threads if name.lower() in thread.name.lower()]
    return threads


class AbstractThreadTask(abc.ABC):
    """
    Thread task abstraction.
    Use this class to define how to execute a task inside the ThreadPool.
    """
    @abc.abstractmethod
    def execute(self) -> None:
        """
        Execution called by the ThreadWorkers on the ThreadPool implementation.
        """


class ThreadWorker(th.Thread):
    """
    Thread pool worker.
    This represents a single thread on the pool. The thread is set as daemon or not based on
    the pool configurations.
    """
    def __init__(self, name: str, tasks: queue.Queue, timeout: float) -> None:
        """
        Class initialization.

        :param str name:        Worker name.
        :param Queue tasks:     Queue to get the tasks from.
        :param float timeout:   Timeout for waiting for a task.
        """
        super().__init__(name=name)
        self._active    = True
        self._queue     = tasks
        self._timeout   = timeout
        SDK_LOG.debug(f"Worker thread {self.name} created.")

    def stop(self) -> None:
        """
        Stops the thread.
        """
        self._active = False

    def run(self) -> None:
        """
        Runs the worker logic.

        - Blocks until retrieves a task from the tasks queue (locked).
        - Checks that the task is a callable and execute.

        """
        # Worker execution
        SDK_LOG.debug(f"Worker thread {self.name} started.")
        while self._active:
            try:
                task = self._queue.get(timeout=self._timeout)
                if isinstance(task, AbstractThreadTask):
                    try:
                        task.execute()
                    except Exception as ex:
                        SDK_LOG.info(
                            f"Caught exception while running task:\n"
                            f"> Task   : {task}\n"
                            f"> Raised : {ex.__class__.__name__} {ex}"
                            )
                    finally:
                        self._queue.task_done()
            except queue.Empty:
                pass

        # Worker termination
        SDK_LOG.debug(f"Worker thread {self.name} terminated.")


class ThreadPool:
    """
    Simple thread pool implementation.
    Use queues to coordinate tasks among a set of worker threads.
    """
    def __init__(self, size: int, name: str, timeout: float = 0.1, daemon: bool = True) -> None:
        """
        Class initialization.

        :param int size:        Size of the thread pool.
        :param str name:        Thread pool name. Used as prefix on the workers as <name>_<worker_id>.
        :param float timeout:   Polling time used by the workers while waiting on a get() request
                                on the task queue. This value mainly affects the time used by the
                                threads to terminate when terminate() is called.
        :param bool daemon:     Set to true if the threads should immediately terminate when the
                                main thread exists.

        :raises ValueError:     Minimum workers count is not met. Polling timeout needs to be a positive number.
        """
        # Input checking
        if size < 1:
            raise ValueError("Thread pool should have at least one worker")
        if timeout <= 0:
            raise ValueError("Polling timeout should be greater than zero")

        # Set attributes
        self._size      = size
        self._prefix    = name
        self._timeout   = timeout
        self._daemon    = daemon
        self._rlock     = th.RLock()
        self._tasks     = queue.Queue()
        self._workers:  tp.List[ThreadWorker] = []

        # Create workers
        self._create_workers()

    def __del__(self):
        """
        Class destructor.
        Ensures that all the workers are terminated.
        """
        try:
            self.stop()
        except AttributeError:
            pass

    @property
    def size(self) -> int:
        """
        Number of workers.
        """
        return self._size

    @property
    def active(self) -> int:
        """
        Number of active workers.
        """
        return sum([worker.is_alive() for worker in self._workers])

    @sync(lock_name="_rlock")
    def enqueue(self, task: AbstractThreadTask) -> None:
        """
        Enqueue a task on the thread pool to be executed by the workers.

        :param AbstractThreadTask task: Task to added to the queue.
        """
        # Check input
        if not isinstance(task, AbstractThreadTask):
            raise ValueError(f"The task need to be {AbstractThreadTask.__name__} or a subclass of it")
        # Enqueue
        self._tasks.put(task)

    @sync(lock_name="_rlock")
    def stop(self) -> None:
        """
        Wait for the task queue to be completed and stop all the workers.
        """
        SDK_LOG.debug("Waiting for all the tasks to be handled...")
        self._tasks.join()
        SDK_LOG.debug("Terminating worker threads...")
        for worker in self._workers:
            worker.stop()

    def _create_workers(self) -> None:
        """
        Create all the pool workers.
        """
        while len(self._workers) < self._size:
            worker = ThreadWorker(
                        name=f"{self._prefix}_{(len(self._workers) + 1)}",
                        tasks=self._tasks, timeout=self._timeout,
                        )
            worker.setDaemon(self._daemon)
            worker.start()
            self._workers.append(worker)


class SimpleThreadTask(AbstractThreadTask):
    """
    Simple thread task.
    Accepts a function to be executed by a worker on the ThreadPool.
    """
    def __init__(self,
                 task: CBAny2None, *args,
                 name: str = "Unnamed", **kwargs) -> None:
        """
        Class initialization.

        :param Callable[..., None] task:    Task functionality.
        :param str name:                    Task name.
        :param args:                        Task arguments.
        :param kwargs:                      Task keyword arguments.
        """
        # Check input
        if not callable(task):
            raise ValueError("The task is not a valid function")

        # Store attributes
        self._name   = name
        self._task   = task
        self._args   = args
        self._kwargs = kwargs

    def __repr__(self) -> str:
        """
        Representation string.
        """
        return f"{self.__class__.__name__}(name={self._name}, task={self._task.__name__})"

    def execute(self) -> None:
        """
        Execution called by the ThreadWorkers on the ThreadPool implementation.
        """
        self._task(*self._args, **self._kwargs)


# -->> Instances <<--------------------
#: Embutils internal thread pool
SDK_TP = ThreadPool(size=10, name="EMBUTILS_Thread_")


# -->> Export <<-----------------------
__all__ = [
    "sync",
    "get_threads",
    "AbstractThreadTask",
    "ThreadWorker",
    "ThreadPool",
    "SimpleThreadTask",
    "SDK_TP",
    ]
