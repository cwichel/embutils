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
from embutils.core import EventException, Events, EventSlot


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
def test_callback1():
    """Test callback."""


def test_callback2():
    """Test callback."""


class EventSlotTestSuite(ut.TestCase):
    def setUp(
        self,
    ) -> None:
        """Set up the test suite."""
        self.slot1 = EventSlot(name="on_change")
        self.slot1 += test_callback1
        self.slot1 += test_callback2
        self.slot2 = EventSlot(name="on_edit")
        self.slot2 += test_callback1

    def test_type(
        self,
    ) -> None:
        """Test the type of the event."""
        self.assertIsInstance(self.slot1, EventSlot)
        self.assertEqual(self.slot1.__name__, "on_change")

    def test_len(
        self,
    ) -> None:
        """Test the length of the event."""
        self.assertEqual(len(self.slot1), 2)
        self.assertEqual(len(self.slot2), 1)

    def test_repr(
        self,
    ) -> None:
        """Test the representation of the event."""
        self.assertEqual(repr(self.slot1), "EventSlot(name='on_change')")
        self.assertEqual(repr(self.slot2), "EventSlot(name='on_edit')")

    def test_iter(
        self,
    ) -> None:
        """Test the iteration of the event."""
        idx = 0
        for target in self.slot1:
            self.assertEqual(target.__name__, f"test_callback{idx + 1}")
            idx += 1

    def test_isub(
        self,
    ) -> None:
        """Test the unsubscription of the event."""
        self.slot1 -= test_callback1
        self.assertEqual(len(self.slot1), 1)
        self.slot1 -= test_callback2
        self.assertEqual(len(self.slot1), 0)
        self.slot1 -= test_callback2
        self.assertEqual(len(self.slot1), 0)


class EventTestSuite(ut.TestCase):
    def test_type(
        self,
    ) -> None:
        """Test the type of the event."""

        class TestEventSlot(EventSlot):
            pass

        events = Events()
        events.on_change += test_callback1
        self.assertEqual(events.etype, EventSlot)
        self.assertIsInstance(events.on_change, EventSlot)

        events = Events(etype=TestEventSlot)
        events.on_change += test_callback1
        self.assertEqual(events.etype, TestEventSlot)
        self.assertIsInstance(events.on_change, TestEventSlot)

    def test_len(
        self,
    ) -> None:
        """Test the length of the event."""
        events = Events()
        self.assertEqual(len(events), 0)
        events.on_change += test_callback1
        self.assertEqual(len(events), 1)
        events.on_change += test_callback2
        self.assertEqual(len(events), 1)
        events.on_edit += test_callback1
        self.assertEqual(len(events), 2)

    def test_getAttr(
        self,
    ) -> None:
        """Test the attribute access of the event."""

        class TestEvents(Events):
            __events__ = ["on_change"]

        with self.assertRaises(EventException):
            TestEvents().on_delete += test_callback1

    def test_iter(
        self,
    ) -> None:
        """Test the iteration of the event."""
        events = Events()
        events.on_change += test_callback1
        events.on_change += test_callback2
        events.on_edit += test_callback1
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
