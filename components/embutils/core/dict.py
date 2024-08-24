#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Alternative dictionaries implementations.

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
_AT = tp.TypeVar("_AT")
"""Alias type variable."""

_KT = tp.TypeVar("_KT")
"""Key type variable."""

_VT = tp.TypeVar("_VT")
"""Value type variable."""


class DictAlias(dict):
    """Dictionary with aliasing capabilities."""

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the dictionary."""
        super().__init__(*args, **kwargs)
        self._aliases = {}

    def __contains__(
        self,
        key: _KT,
    ) -> bool:
        """Check if the dictionary contains a key."""
        return super().__contains__(self.get_key(key=key))

    def __delitem__(
        self,
        key: _KT,
    ) -> None:
        """Delete an item from the dictionary."""
        key = self.get_key(key=key)
        aliases = self.get_alias(key=key)
        super().__delitem__(key)
        for alias in aliases:
            del self._aliases[alias]

    def __getitem__(
        self,
        key: _KT,
    ) -> _VT:
        """Get an item from the dictionary."""
        return super().__getitem__(self.get_key(key=key))

    def __setitem__(
        self,
        key: _KT,
        value: _VT,
    ) -> None:
        """Set an item in the dictionary."""
        super().__setitem__(self.get_key(key=key), value)

    def get(
        self,
        key: _KT,
        default: tp.Optional[_VT] = None,
    ) -> tp.Optional[_VT]:
        """Get an item from the dictionary."""
        return super().get(self.get_key(key=key), default)

    def pop(
        self,
        key: _KT,
    ) -> tp.Optional[_VT]:
        """Pop an item from the dictionary."""
        key = self.get_key(key=key)
        aliases = self.get_alias(key=key)
        for alias in aliases:
            del self._aliases[alias]
        return super().pop(key)

    def popitem(
        self,
    ) -> tp.Tuple[_KT, _VT]:
        """Pop an item from the dictionary."""
        key, item = super().popitem()
        aliases = self.get_alias(key=key)
        for alias in aliases:
            del self._aliases[alias]
        return key, item

    def update(
        self,
        m: tp.Union[tp.Mapping[_KT, _VT], tp.Iterable[tp.Tuple[_KT, _VT]]] = None,
        **kwargs,
    ) -> None:
        """Update the dictionary."""
        if m is not None:
            for key, value in m.items() if isinstance(m, dict) else m:
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def set_alias(
        self,
        key: _KT,
        alias: _AT,
    ) -> None:
        """Set an alias."""
        self._aliases[alias] = key

    def get_alias(
        self,
        key: _KT,
    ) -> tp.List[_AT]:
        """Get the aliases for a key."""
        return [alias for alias, value in self._aliases.items() if (value == key)]

    def del_alias(
        self,
        alias: _AT,
    ) -> None:
        """Delete an alias."""
        del (self._aliases[alias],)

    def get_key(
        self,
        key: tp.Union[_AT, _KT],
    ) -> tp.Optional[_KT]:
        """Get the key for an alias."""
        return self._aliases.get(key, key)


# -->> API <<---------------------------


# -->> Export <<------------------------
__all__ = [
    "DictAlias",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
