#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""C#-like event handling system.

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
import typing as tp


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
@tp.runtime_checkable
class EventTarget(tp.Protocol):
    """Event target protocol."""

    def __call__(
        self,
        *args,
        **kwargs,
    ) -> tp.Optional[tp.Any]:
        """Event handler.

        This function can return a value, but it will be ignored.

        :param args: Event arguments.
        :param kwargs: Event keyword arguments.
        """


class EventException(Exception):
    """Base class for exceptions in this module."""


class EventSlot:
    """Define a single event.

    :param name: Name of the event.
    """

    def __init__(
        self,
        name: str,
    ) -> None:
        """Initialize the event."""
        self.targets: tp.List[EventTarget] = []
        self.__name__ = name

    def __repr__(
        self,
    ) -> str:
        """Return a string representation of the event."""
        return f"{self.__class__.__name__}(name={self.__name__!r})"

    def __len__(
        self,
    ) -> int:
        """Return the number of targets."""
        return len(self.targets)

    def __call__(
        self,
        *args,
        **kwargs,
    ) -> None:
        """Fire the event.

        :param args: Event arguments.
        :param kwargs: Event keyword arguments.
        """
        for target in self.targets:
            target(*args, **kwargs)

    def __iter__(
        self,
    ) -> tp.Iterator[EventTarget]:
        """Return an iterator over the event targets."""
        for target in self.targets:
            yield target

    def __iadd__(
        self,
        target: EventTarget,
    ) -> "EventSlot":
        """Add a target to the event.

        :param target: Event target.
        """
        self.targets.append(target)
        return self

    def __isub__(
        self,
        target: EventTarget,
    ) -> "EventSlot":
        """Remove all targets with the given callable from the event.

        :param target: Event target.
        """
        while target in self.targets:
            self.targets.remove(target)
        return self

    __str__ = __repr__
    """Ensure a readable string representation of the event."""


class Events:
    """Encapsulates the event subscription and firing.

    .. note::

        - Event slots are created/added automatically, so there is no need to
          declare/create them beforehand (Note that `__events__` is optional
          and should be used primarily to avoid misspelling).
        - Main goal of this class is to avoid the redundancy in calls like::

            <class>.on_change = EventSlot("on_change")

    :param events: List of events.
    :param etype: Event type used to create new slots.
    """

    def __init__(
        self,
        events: tp.List[str] = None,
        etype: tp.Type[EventSlot] = EventSlot,
    ) -> None:
        self.etype = etype
        if events is not None:
            try:
                self.__events__ = [etype(name=str(event)) for event in events]
            except Exception:
                raise AttributeError("Invalid events. Please validate that is an iterable with event names.")

    def __repr__(
        self,
    ) -> str:
        """Return a string representation of the events."""
        return f"{self.__class__.__name__}(etype={self.etype.__name__})"

    def __len__(
        self,
    ) -> int:
        """Return the number of events."""
        return len(list(self.__iter__()))

    def __iter__(
        self,
    ) -> tp.Iterator[EventSlot]:
        """Return an iterator over the events."""
        for _, item in self.__dict__.items():
            if isinstance(item, EventSlot):
                yield item

    def __getattr__(
        self,
        item: str,
    ) -> EventSlot:
        """Return the event with the given name.

        :param item: Event name.
        """
        if item.startswith("__"):
            raise AttributeError(f"{self.__class__.__name__} has no attribute {item}.")
        if hasattr(self, "__events__") and (item not in self.__events__):
            raise EventException(f"Event {item} is not declared.")
        if item not in self.__dict__:
            self.__dict__[item] = self.etype(name=item)
        return self.__dict__[item]

    def __getitem__(
        self,
        item: str,
    ) -> EventSlot:
        """Return the event with the given name.

        :param item: Event name.
        """
        if item not in self.__dict__:
            return self.__getattr__(item=item)
        return self.__dict__[item]

    __str__ = __repr__
    """Ensure a readable string representation of the event."""


# -->> API <<---------------------------


# -->> Export <<------------------------
__all__ = [
    "EventTarget",
    "EventException",
    "EventSlot",
    "Events",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
