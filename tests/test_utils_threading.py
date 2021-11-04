#!/usr/bin/python
# -*- coding: ascii -*-
"""
Threading utilities testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import time

import pytest
import unittest

from embutils.utils import SDK_LOG, ThreadPool, SimpleThreadTask, get_threads


# -->> Definitions <<------------------


# -->> Test API <<---------------------
class TestThreading(unittest.TestCase):
    """
    Test threading utilities.
    """
    def test_01_pool_fail(self):
        """
        Test pool failure cases.
        """
        # No workers
        with pytest.raises(ValueError):
            ThreadPool(size=0, name="ThreadPoolTest01")

        # Timeout not supported
        with pytest.raises(ValueError):
            ThreadPool(size=1, name="ThreadPoolTest01", timeout=0)

    def test_02_pool_size_check(self):
        """
        Test if the number of workers match the initial configuration
        """
        # Check number of workers being created
        tp = ThreadPool(size=5, name="ThreadPoolTest02")
        assert tp.size == 5

        # Check number of workers
        tn = get_threads(name="ThreadPoolTest02")
        assert len(tn) == tp.size

    def test_03_pool_daemon_check(self):
        """
        Test if threads are being created with the correct daemon configuration.
        """
        # Check threads being created as daemon
        ThreadPool(size=5, name="ThreadPoolTest03_01", daemon=True)
        tn = get_threads(name="ThreadPoolTest03_01")
        assert tn.pop().daemon is True

        tp = ThreadPool(size=5, name="ThreadPoolTest03_02", daemon=False)
        tn = get_threads(name="ThreadPoolTest03_02")
        assert tn.pop().daemon is False
        tp.stop()

    def test_04_pool_workers_stop(self):
        """
        Test the thread pool stop functionality.
        """
        # Check if workers stop when required
        tp = ThreadPool(size=5, name="ThreadPoolTest04", daemon=False)
        tp.stop()
        while tp.active:
            time.sleep(0.1)
        assert tp.active == 0

    def test_05_task_fail(self):
        """
        Test task failure cases.
        """
        # Check faulty task creation
        with pytest.raises(ValueError):
            SimpleThreadTask(task=None)

        # Check faulty task enqueue
        tp = ThreadPool(size=5, name="ThreadPoolTest05")
        with pytest.raises(ValueError):
            tp.enqueue(task=None)


# -->> Test Execution <<---------------
if __name__ == '__main__':
    SDK_LOG.enable()
    unittest.main()
