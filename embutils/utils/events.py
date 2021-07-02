#!/usr/bin/python
# -*- coding: ascii -*-
"""
Event handling utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""


class EventHook:
    """
    Event hook abstraction. This utility allows to emit custom states to several
    callbacks in a simple fashion.

    .. note::
        *   All the callbacks subscribed to a hook need to handle the same arguments.
    """

    def __init__(self):
        """
        This class don't require any input from the user to be initialized.
        """
        self._callbacks = []

    def __iadd__(self, callback: callable) -> 'EventHook':
        """
        Simplified callback subscription. Overrides the **+=** operator.

        :param callable callback: Event callback.

        :returns: Self.
        :rtype: EventHook
        """
        self.subscribe(callback=callback)
        return self

    def __isub__(self, callback: callable) -> 'EventHook':
        """
        Simplified callback unsubscription. Overrides the **-=** operator.

        :param callable callback: Event callback.

        :returns: Self.
        :rtype: EventHook
        """
        self.unsubscribe(callback=callback)
        return self

    @property
    def empty(self) -> bool:
        """
        Checks if the event hook has callbacks subscribed.

        :returns: True if the hook has no callbacks, false otherwise.
        :rtype: bool
        """
        return len(self._callbacks) == 0

    def subscribe(self, callback: callable) -> bool:
        """
        Subscribes a callback to the event hook.

        :param callable callback: Event callback.

        :returns: True if subscribed, false otherwise.
        :rtype: bool
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)
            return True
        return False

    def unsubscribe(self, callback: callable) -> bool:
        """
        Unsubscribes a callback from the event hook.

        :param callable callback: Event callback.

        :returns: True if unsubscribed, false otherwise.
        :rtype: bool
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            return True
        return False

    def clear(self) -> None:
        """
        Remove all the callbacks from the hook.
        """
        self._callbacks.clear()

    def emit(self, *args, **kwargs) -> None:
        """
        Emit the given arguments to all the callbacks.

        :param args: Arguments.
        :param kwargs: Key arguments.
        """
        for callback in self._callbacks:
            callback(*args, **kwargs)
