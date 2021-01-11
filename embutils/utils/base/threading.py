from threading import Lock, Thread
from typing import Union


class ThreadItem(Thread):
    """Thread implementation.
    All the threads created using this class (daemons or not) can be
    monitored using the ThreadPool class.
    """
    def __init__(self, name: str = 'Unnamed', daemon: bool = True, *args, **kwargs):
        super(ThreadItem, self).__init__(name=name, *args, **kwargs)
        self.setDaemon(daemon)
        self.start()

    def run(self) -> None:
        """Run the thread process.
        """
        ThreadPool().add(thread=self)
        super().run()
        ThreadPool().remove(thread=self)


class ThreadPool(object):
    """Simple thread pool implementation.
    This class is implemented as a singleton.
    """
    MAX_THREADS:    int = 100

    __inst:         Union[None, 'ThreadPool'] = None

    def __new__(cls):
        """Singleton creation.
        """
        if cls.__inst is None:
            cls.__inst = super(ThreadPool, cls).__new__(cls)
        return cls.__inst

    def __init__(self):
        """Class constructor.
        """
        # Initialize
        self._lock = Lock()
        self._total = 0
        self._details = dict()

    @property
    def total(self) -> int:
        """Return the number of threads being executed.

        Return:
            int: Number of threads.
        """
        with self._lock:
            return self._total

    @property
    def details(self) -> list:
        """Return a list with the quantity and type of the
        threads running.

        Return:
            list: Type/quantity of threads running.
        """
        with self._lock:
            fmt = '{{key:<{size}s}}: {{val:d}}'.format(size=max([len(key) for key in list(self._details.keys())]))
            return [fmt.format(key=key, val=val) for key, val in self._details.items()]

    def add(self, thread: Thread) -> None:
        """Add a thread to the running pool.

        Args:
            thread (Thread): Thread to be added.
        """
        with self._lock:
            # Check the number of threads...
            self._total += 1
            if self._total > self.MAX_THREADS:
                raise ThreadOverflowException()

            # All Ok. Add thread.
            if thread.name in self._details:
                self._details[thread.name] += 1
            else:
                self._details[thread.name] = 1

    def remove(self, thread: Thread) -> None:
        """Remove a thread from the running pool.

        Args:
            thread (Thread): Thread to be removed.
        """
        with self._lock:
            self._total -= 1
            if thread.name in self._details:
                self._details[thread.name] -= 1
                if self._details[thread.name] == 0:
                    self._details.pop(thread.name)


class ThreadOverflowException(Exception):
    """Thread overflow exception.
    """
    def __init__(self):
        super().__init__(
            'Maximum number of threads exceeded ({})'.format(ThreadPool().MAX_THREADS) +
            '\nThread details:\n\t' + '\n\t'.join(ThreadPool().details) + '\n'
            )
