#!/usr/bin/python
# -*- coding: ascii -*-
"""
SDK threading utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

from abc import ABC, abstractmethod
from functools import wraps
from queue import Empty, Queue
from threading import RLock, Thread
from typing import Callable, List, TypeVar

from .logger import SDK_LOG


# -->> Definitions <<------------------
RT = TypeVar('RT')


# -->> API <<--------------------------
def sync(lock_name: str) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """
    Decorator used to wrap a class method with a lock defined as
    instance/class attribute.

    :param str lock_name: Name of the lock attribute.

    :returns: Locked function.
    :rtype: Callable[[Callable[..., RT]], Callable[..., RT]]
    """
    def wrapper(func: Callable[..., RT]) -> Callable[..., RT]:
        """
        Wraps the decorated function to apply the lock.
        """
        @wraps(func)
        def synchronizer(self, *args, **kwargs) -> RT:
            """
            Applies a lock over the given function.
            """
            lock = self.__getattribute__(lock_name)
            with lock:
                return func(self, *args, **kwargs)
        return synchronizer
    return wrapper


class _ThreadWorker(Thread):
    """
    Thread pool worker.
    This represents a single thread on the pool. The thread is set as daemon or not based on
    the pool configurations.
    """
    def __init__(self, name: str, queue: Queue, timeout: float) -> None:
        """
        Class initialization.

        :param str name:        Worker name.
        :param Queue queue:     Queue to get the tasks from.
        :param float timeout:   Timeout for waiting for a task.
        """
        super().__init__(name=name)
        SDK_LOG.debug(f"Creating worker thread {self.name}")
        self._active = True
        self._queue = queue
        self._timeout = timeout

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
        while self._active:
            try:
                task = self._queue.get(timeout=self._timeout)
                if isinstance(task, AbstractThreadTask):
                    try:
                        task.execute()
                    except Exception as ex:
                        SDK_LOG.info(f"Caught exception while running task:\n"
                                     f"> Task   : {task}\n"
                                     f"> Raised : {ex.__class__.__name__} {ex}")
                    finally:
                        self._queue.task_done()
            except Empty:
                pass

        # Worker termination
        SDK_LOG.debug(f"Terminating worker thread {self.name}")


class AbstractThreadTask(ABC):
    """
    Thread task abstraction.
    Use this class to define how to execute a task inside the ThreadPool.
    """
    @abstractmethod
    def execute(self) -> None:
        """
        Execution called by the ThreadWorkers on the ThreadPool implementation.
        """


class SimpleThreadTask(AbstractThreadTask):
    """
    Simple thread task.
    Accepts a function to be executed by a worker on the ThreadPool.
    """
    def __init__(self, task: Callable[..., None], *args, name: str = 'Unnamed', **kwargs) -> None:
        """
        Task configuration:

        :param Callable[..., None] task:    Task function.
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


class ThreadPool:
    """
    Simple thread pool implementation.
    Use queues to coordinate tasks among a set of worker threads.
    """
    def __init__(self, size: int, name: str, timeout: float = 60, daemon: bool = True) -> None:
        """
        :param int size:        Size of the thread pool.
        :param str name:        Thread pool name. Used as prefix on the workers as <name>_<worker_id>.
        :param float timeout:   Polling time used by the workers while waiting on a get() request
                                on the task queue. This value mainly affects the time used by the
                                threads to terminate when terminate() is called.
        :param bool daemon:     Set to true if the threads should immediately terminate when the
                                main thread exists.
        """
        # Input checking
        if size < 1:
            raise ValueError("Thread pool should have at least one worker")
        if timeout <= 0:
            raise ValueError("Polling timeout should be greater than zero")

        # Set attributes
        self._size = size
        self._daemon = daemon
        self._prefix = name
        self._timeout = timeout
        self._rlock = RLock()
        self._queue = Queue()
        self._workers: List[_ThreadWorker] = []

        # Create workers
        self._create_workers()

    @property
    @sync(lock_name='_rlock')
    def size(self) -> int:
        """
        Size of the thread pool.
        """
        return self._size

    def enqueue(self, task: AbstractThreadTask) -> None:
        """
        Enqueue a task on the thread pool to be executed by the workers.

        :param AbstractThreadTask task: Task to added to the queue.
        """
        # Check input
        if not isinstance(task, AbstractThreadTask):
            raise ValueError(f"The task need to be {AbstractThreadTask.__name__} or a subclass of it")
        # Enqueue
        self._queue.put(task)

    @sync(lock_name='_rlock')
    def stop(self) -> None:
        """
        Wait for the task queue to be completed and stops all the workers.
        """
        SDK_LOG.debug("Waiting for all the tasks to be handled...")
        self._queue.join()
        SDK_LOG.debug("Terminating worker threads...")
        for worker in self._workers:
            worker.stop()

    @sync(lock_name='_rlock')
    def _create_workers(self) -> None:
        """
        Create all the pool workers.
        """
        while len(self._workers) < self._size:
            worker = _ThreadWorker(name=f"{self._prefix}_{(len(self._workers) + 1)}", queue=self._queue, timeout=self._timeout)
            worker.setDaemon(self._daemon)
            worker.start()
            self._workers.append(worker)


# -->> Instances <<--------------------
#: Embutils internal thread pool
SDK_TP = ThreadPool(size=4, name='EMBUTILS_Thread_', timeout=30)
