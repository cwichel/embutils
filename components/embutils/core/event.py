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
        :return: Any value.
        """


class EventSlot:
    """Event slot. Allows to propagate events to multiple targets.

    :param name: Name of the event.
    """

    def __init__(
        self,
        name: str,
    ) -> None:
        """Class constructor."""
        self.targets: tp.List[EventTarget] = []
        self.__name__ = name

    def __repr__(
        self,
    ) -> str:
        """Object representation."""
        return f"{self.__class__.__name__}(name={self.__name__!r})"

    def __len__(
        self,
    ) -> int:
        """Number of targets."""
        return len(self.targets)

    def __call__(
        self,
        *args,
        **kwargs,
    ) -> None:
        """Emits the event.

        :param args: Event arguments.
        :param kwargs: Event keyword arguments.
        """
        for target in self.targets:
            target(*args, **kwargs)

    def __iter__(
        self,
    ) -> tp.Iterator[EventTarget]:
        """Iterable with event targets."""
        for target in self.targets:
            yield target

    def __iadd__(
        self,
        target: EventTarget,
    ) -> "EventSlot":
        """Attach a new target to the event.

        :param target: Event target.
        """
        if target not in self.targets:
            self.targets.append(target)
        return self

    def __isub__(
        self,
        target: EventTarget,
    ) -> "EventSlot":
        """Detach a target from the event.

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

        - Event slots are created/added automatically, so there is no need to declare/create them beforehand.
        - Main goal of this class is to avoid the redundancy in calls like::

            <class>.on_change = EventSlot("on_change")

    :param events: List of events. The class can't have more events than the ones declared here.
    :param etype: Event type used to create new slots.
    """

    def __init__(
        self,
        events: tp.List[str] = None,
        etype: tp.Type[EventSlot] = EventSlot,
    ) -> None:
        """Class constructor."""
        if etype is None or not issubclass(etype, EventSlot):
            raise AttributeError("Invalid event type. Please validate that is a subclass of EventSlot.")
        # Prepare
        self.__etype__ = etype
        # Initialize
        if events is not None:
            if not (isinstance(events, tp.Iterable) and all(isinstance(event, str) for event in events)):
                raise AttributeError("Invalid events. Please validate that is an iterable with event names.")
            self.__events__ = events

    def __repr__(
        self,
    ) -> str:
        """Object representation."""
        return f"{self.__class__.__name__}(etype={self.__etype__.__name__})"

    def __len__(
        self,
    ) -> int:
        """Number of event slots."""
        return len(list(self.__iter__()))

    def __iter__(
        self,
    ) -> tp.Iterator[EventSlot]:
        """Iterable with event slots."""
        for _, value in self.__dict__.items():
            if isinstance(value, EventSlot):
                yield value

    def __getattr__(
        self,
        item: str,
    ) -> EventSlot:
        """Get an attribute using dot notation: "object.item" when "item" is not found by __getattribute__.

        :param item: Attribute to get.

        :return: Attribute value.
        """
        # No events with private names
        if item.startswith("__"):
            raise AttributeError(f"Has no attribute '{item}'.")
        # Check if events are limited
        if hasattr(self, "__events__") and item not in self.__events__:
            raise AttributeError(f"Event '{item}' is not declared.")
        # Create/get event
        self.__dict__[item] = event = self.__etype__(item)
        return event

    def __getitem__(
        self,
        item: str,
    ) -> EventSlot:
        """Get an attribute using indexing: "object["item"]"

        :param item: Attribute to get.

        :return: Attribute value.
        """
        return self.__getattr__(item=item)

    __str__ = __repr__
    """Ensure a readable string representation of the event."""


# -->> API <<---------------------------


# -->> Export <<------------------------
__all__ = [
    "EventTarget",
    "EventSlot",
    "Events",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
