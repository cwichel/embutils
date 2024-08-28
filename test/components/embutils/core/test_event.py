#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Bit manipulation utilities test suite.

:date:      2024
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# --------------------------------------
__author__ = "Christian Wiche"
__version__ = "ALPHA"
# --------------------------------------

# Built-in
import unittest as ut

# External
from embutils.core import Events, EventSlot


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
TEST_CALLS = []
"""Test calls."""


def callback1():
    """Test callback."""
    TEST_CALLS.append(1)


def callback2():
    """Test callback."""
    TEST_CALLS.append(2)


class EventSlotTestSuite(ut.TestCase):
    def setUp(
        self,
    ) -> None:
        """Set up the test suite."""
        global TEST_CALLS
        TEST_CALLS = []
        self.slot1 = EventSlot(name="on_edit")
        self.slot2 = EventSlot(name="on_change")
        self.slot2 += callback1
        self.slot2 += callback2

    def test_type(
        self,
    ) -> None:
        """Test the type of the event."""
        self.assertIsInstance(self.slot1, EventSlot)
        self.assertEqual(self.slot1.__name__, "on_edit")
        self.assertIsInstance(self.slot2, EventSlot)
        self.assertEqual(self.slot2.__name__, "on_change")

    def test_len(
        self,
    ) -> None:
        """Test the length of the event."""
        self.assertEqual(len(self.slot1), 0)
        self.assertEqual(len(self.slot2), 2)

    def test_repr(
        self,
    ) -> None:
        """Test the representation of the event."""
        self.assertEqual(repr(self.slot1), "EventSlot(name='on_edit')")
        self.assertEqual(repr(self.slot2), "EventSlot(name='on_change')")

    def test_iter(
        self,
    ) -> None:
        """Test the iteration of the event."""
        targets = list(self.slot2)
        self.assertEqual(len(targets), 2)
        self.assertIn(callback1, targets)
        self.assertIn(callback2, targets)

    def test_iadd(
        self,
    ) -> None:
        """Test the subscription of the event."""
        # Subscribe to new items
        self.slot1 += callback1
        self.assertEqual(len(self.slot1), 1)
        self.slot1 += callback2
        self.assertEqual(len(self.slot1), 2)
        # Subscribe to existing items
        self.slot1 += callback1
        self.assertEqual(len(self.slot1), 2)

    def test_isub(
        self,
    ) -> None:
        """Test the unsubscription of the event."""
        # Test unsubscribing from existing items
        self.slot2 -= callback1
        self.assertEqual(len(self.slot2), 1)
        self.slot2 -= callback2
        self.assertEqual(len(self.slot2), 0)
        # Test unsubscribing from non-existing items
        self.slot2 -= callback2
        self.assertEqual(len(self.slot2), 0)

    def test_runTargets(
        self,
    ) -> None:
        """Test the execution of the event."""
        global TEST_CALLS
        self.assertEqual(TEST_CALLS, [])
        self.slot2()
        self.assertEqual(TEST_CALLS, [1, 2])


class EventTestSuite(ut.TestCase):
    def test_init(
        self,
    ) -> None:
        """Test event handler initialization."""

        class TestEventSlot(EventSlot):
            pass

        events = Events(etype=TestEventSlot)
        events.on_change += callback1
        self.assertEqual(events.__etype__, TestEventSlot)
        self.assertIsInstance(events.on_change, TestEventSlot)

        events = Events(events=["on_change", "on_edit"])
        self.assertIsInstance(events.on_edit, EventSlot)
        self.assertIsInstance(events["on_change"], EventSlot)
        with self.assertRaises(AttributeError):
            events.__on_private += callback1
        with self.assertRaises(AttributeError):
            events.on_delete += callback1

        with self.assertRaises(AttributeError):
            Events(etype=None)
        with self.assertRaises(AttributeError):
            Events(events=[1, 2, 3])

    def test_len(
        self,
    ) -> None:
        """Test the length of the event."""
        events = Events()
        self.assertEqual(len(events), 0)
        events.on_change += callback1
        self.assertEqual(len(events), 1)
        events.on_change += callback2
        self.assertEqual(len(events), 1)
        events.on_edit += callback1
        self.assertEqual(len(events), 2)

    def test_iter(
        self,
    ) -> None:
        """Test the iteration of the event."""
        events = Events()
        events.on_change += callback1
        events.on_change += callback2
        events.on_edit += callback1
        idx = 0
        for event in events:
            self.assertIsInstance(event, EventSlot)
            idx += 1
        self.assertEqual(idx, len(events))


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
