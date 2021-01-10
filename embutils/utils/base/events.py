class EventHook:
    """Utility that allows to subscribe multiple callbacks
    to a single event. When the event is emitted the given
    inputs are propagated to all the registered callbacks.

    NOTE: All the callbacks added to the hook need to have
    the same arguments.
    """
    def __init__(self):
        """Class constructor. Initialize the handlers list.
        """
        self._handlers = []

    def __iadd__(self, handler: callable) -> 'EventHook':
        """Operator += implementation.
        Adds a function handler to the event hook.

        Args:
            handler (callable): Function handler.

        Returns:
            EventHook: self.
        """
        if handler not in self._handlers:
            self._handlers.append(handler)
        return self

    def __isub__(self, handler: callable) -> 'EventHook':
        """Operator -= implementation.
        Removes a function handler from the event hook.

        Args:
            handler (callable): Function handler.

        Returns:
            EventHook: self.
        """
        if handler not in self._handlers:
            self._handlers.remove(handler)
        return self

    @property
    def empty(self) -> bool:
        """Return if the event hook is empty.

        Returns:
            bool: True if the hook has no handlers.
        """
        return len(self._handlers) == 0

    def clear(self) -> None:
        """Clears the handlers array.
        """
        self._handlers.clear()

    def emit(self, *args, **kwargs) -> None:
        """Emits all the handlers with the given arguments.
        """
        for handler in self._handlers:
            handler(*args, **kwargs)
