#!/usr/bin/python
# -*- coding: ascii -*-
"""
Threading utilities testing.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import pytest
import threading
import unittest

from embutils.utils import ThreadPool, SimpleThreadTask


# Test Utilities ================================
def get_threads_with_name(name: str) -> dict:
    """
    Return all the live threads that match with the given name.

    :param str name: Name of the threads to get.

    :returns: Dictionary with named threads that match.
    :rtype: dict
    """
    live_threads = threading.enumerate()
    named_threads = {}
    for live_thread in live_threads:
        if name in live_thread.name:
            named_threads[live_thread.name] = live_thread
    return named_threads


# Test Definitions ==============================
class TestByte(unittest.TestCase):
    """
    Test threading utilities.
    """
    def test_01_pool_value_check(self):
        with pytest.raises(ValueError):
            ThreadPool(size=0, name="ThreadPoolTest")

        with pytest.raises(ValueError):
            ThreadPool(size=1, name="ThreadPoolTest", timeout=0)

    def test_02_pool_size_check(self):
        tp = ThreadPool(size=5, name="ThreadPoolTest")
        assert tp.size == 5

        tn = get_threads_with_name(name="ThreadPoolTest")
        assert len(tn.keys()) == tp.size

    def test_03_pool_daemon_check(self):
        ThreadPool(size=5, name="ThreadPoolTest", daemon=True)
        tn = get_threads_with_name(name="ThreadPoolTest")
        n, t = tn.popitem()
        assert t.daemon is True

    def test_04_pool_task_check(self):
        tp = ThreadPool(size=5, name="ThreadPoolTest")
        with pytest.raises(ValueError):
            tp.enqueue(task=None)

    def test_05_simpletask_check(self):
        with pytest.raises(ValueError):
            SimpleThreadTask(task=None)


# Test Execution ================================
if __name__ == '__main__':
    unittest.main()
