#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Entity-Component System (ECS) implementation.

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
import functools as ft
import typing as tp
import uuid as ud
import weakref as wr

# External
import embutils.core as sc
import pydantic as pdt

# App
from .model import BaseModel


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
_CT = tp.TypeVar("_CT", bound="Component")
"""Component type variable."""

_ET = tp.TypeVar("_ET", bound="Entity")
"""Entity type variable."""


class Component(BaseModel):
    """Component implementation.

    A component is a data/functionality container that grant an entity with extended
    capabilities.

    :param entity: Entity to bind to.
    """

    ETYPE: tp.ClassVar[tp.Type["Entity"]] = None
    """Entity type that the component can be attached to."""

    entity: wr.ProxyType = pdt.Field(default=None)

    _id: str = pdt.PrivateAttr(default_factory=lambda: str(ud.uuid4()))
    """Component unique identifier."""

    @property
    def id(
        self,
    ) -> str:
        """Return the component unique identifier.

        :return: Component unique identifier.
        """
        return self._id

    def bind(
        self,
        entity: wr.ProxyType,
    ) -> None:
        """Bind an entity to this component.

        :param entity: Entity to bind to.
        """
        etype = self.ETYPE or Entity
        if not issubclass(entity.__class__, etype):
            raise TypeError(f"Entity must be a subclass of {self.ETYPE}")
        self.entity = entity

    def unbind(
        self,
    ) -> None:
        """Unbind the entity from this component."""
        self._unregister_override()

    def _register_override(
        self,
        override: tp.Dict[str, tp.Callable],
    ) -> None:
        """Register a method override.

        :param override: Overrides to register.
        """
        if self.entity:
            self.entity.register_override(source=self.id, override=override)

    def _unregister_override(
        self,
        override: tp.Optional[tp.Set[str]] = None,
    ) -> None:
        """Unregister a method override.

        :param override: Overrides to unregister. If None, all overrides from the source will be unregistered.
        """
        if self.entity:
            self.entity.unregister_override(source=self.id, override=override)


class Entity(BaseModel):
    """Entity implementation.

    An entity represents a general-purpose object that can be extended with components.

    .. note::

        - Entities are not meant to be instantiated directly. Instead, they should be
          subclassed and used as a base for specific entity types.
        - Components are meant to be used as data/functionality containers that grant
          an entity with extended capabilities.
        - This ECS implementation limit the number of components that can be attached
          to an entity to 1 per type.
    """

    EDB: tp.ClassVar[dict] = {}
    """Entity database."""
    CDB: tp.ClassVar[dict] = {}
    """Component database."""

    id: str = pdt.Field(default_factory=lambda: str(ud.uuid4()), exclude=True, frozen=True, init_var=False)
    """Entity unique identifier."""
    components: sc.DictAlias = pdt.Field(default_factory=sc.DictAlias, exclude=True, init_var=False)
    """Entity components."""

    _overrides: tp.Dict[str, tp.Dict[str, tp.Callable]] = pdt.PrivateAttr(default_factory=dict)
    """Entity methods overrides."""

    def __len__(
        self,
    ) -> int:
        """Return the number of components attached to the entity.

        :return: Number of components.
        """
        return len(self.components)

    def __getattr__(
        self,
        item: str,
    ) -> tp.Any:
        """Get an attribute using dot notation: "object.item" when "item" is not found by __getattribute__.

        :param item: Attribute to get.

        :return: Attribute value.
        """
        if out := self.components.get(item, None):
            return out
        return super().__getattr__(item)

    def __getitem__(
        self,
        item: str,
    ) -> tp.Any:
        """Get an attribute using indexing: "object["item"]"

        :param item: Attribute to get.

        :return: Attribute value.
        """
        if out := self.components.get(item, None):
            return out
        raise KeyError(f"Entity {self.id} has no component named {item}.")

    def attach(
        self,
        component: _CT,
        alias: str = None,
    ) -> None:
        """Attach a component to the entity.

        :param component: Component to attach.
        :param alias: Component alias.
        """
        # Get info
        ctp = type(component)
        name = ctp.__name__
        alias = alias or name
        # Check if already attached
        if any([((k in self.components) or (getattr(self, k, None) is not None)) for k in [name, alias, component.id]]):
            raise KeyError(f"Component {name} ({alias}) already attached or with an alias conflict.")
        # Append and bind
        component.bind(entity=self.EDB[self.id])
        self.components[name] = component
        self.components.set_alias(key=name, alias=alias)
        self.components.set_alias(key=name, alias=component.id)
        # Add to component database
        if name not in self.CDB:
            self.CDB[name] = []
        if self.id in self.CDB[name]:
            raise KeyError(f"Component {name} already registered for this entity.")
        self.CDB[name].append(self.id)

    def detach(
        self,
        component: tp.Optional[tp.Union[tp.Type[_CT], _CT, str]] = None,
    ) -> None:
        """Detach a component from the entity.

        :param component: Component to detach. It can be identified by its type, instance, or alias.
        """
        # Get component name(s)
        name = self._get_component_key(component=component)
        if name is None:
            names = list(self.components.keys())
        elif name in self.components:
            names = [name]
        else:
            # Nothing to delete or is unknown to this entity. Just ignore
            return
        # Unbind and delete
        for name in names:
            item = self.components.pop(name)
            item.unbind()
            self.CDB[name].remove(self.id)

    def has(
        self,
        component: tp.Union[tp.Type[_CT], _CT, str],
    ) -> bool:
        """Return whether the entity has the given component attached.

        :param component: Component to check. It can be identified by its type, instance, or alias.

        :return: Whether the entity has the given component attached.
        """
        name = self._get_component_key(component=component)
        return name and (self.components.get(name) is not None)

    def register_override(
        self,
        source: str,
        override: tp.Dict[str, tp.Callable],
    ) -> None:
        """Register a method override.

        :param source: Source of the override.
        :param override: Overrides to register.
        """
        for name, method in override.items():
            # Validate non-attribute
            attrs = set(self.__dict__.keys()) - set(self._overrides.keys())
            if name in attrs:
                raise AttributeError(f"Unable to override an entity attribute: {name}.")
            if self.components.get(name, None) is not None:
                raise AttributeError(f"Unable to override an entity component: {name}.")
            if not callable(method):
                raise TypeError(f"Override {name} must be callable.")
            # Update override DB
            if name not in self._overrides:
                self._overrides[name] = {source: method}
            else:
                self._overrides[name][source] = method
            # Force override execution
            if name not in self.__dict__:
                self.__dict__[name] = ft.partial(self._override_handler, name=name)

    def unregister_override(
        self,
        source: str,
        override: tp.Optional[tp.Set[str]] = None,
    ) -> None:
        """Unregister a method override.

        :param source: Source of the override.
        :param override: Overrides to unregister. If None, all overrides from the source will be unregistered.
        """
        names = override or set(self._overrides.keys())
        for name in names:
            # Ignore keys that are not in the override DB
            if name not in self._overrides:
                continue
            # Remove override
            if source in self._overrides[name]:
                self._overrides[name].pop(source, None)
            # Remove override DB entry if empty
            if not self._overrides[name]:
                self._overrides.pop(name, None)
                self.__dict__.pop(name, None)

    def _override_handler(
        self,
        name: str,
        *args,
        **kwargs,
    ) -> tp.Any:
        """Handle method override.

        :param name: Method name.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.

        :return: Method return value.
        """
        if name in self._overrides:
            source = list(self._overrides[name].keys())[-1]
            return self._overrides[name][source](*args, **kwargs)
        raise AttributeError(f"Method {name} configured for override but not source found.")

    def _get_component_key(
        self,
        component: tp.Optional[tp.Union[tp.Type[_CT], _CT, str]],
    ) -> tp.Optional[str]:
        """Return the component key.

        :param component: Component to get the key from. It can be identified by its type, instance, or alias.

        :return: Component key.
        """
        if isinstance(component, str):
            return self.components.get_key(key=component)
        if isinstance(component, type):
            return component.__name__
        elif isinstance(component, Component):
            return type(component).__name__
        return None

    def _post_init(
        self,
        **kwargs,
    ) -> None:
        # Docstring inherited from BaseModel.
        super()._post_init(**kwargs)
        self.register(entity=self)

    @classmethod
    def get_by_id(
        cls: tp.Type[_ET],
        eid: str,
    ) -> tp.Optional[_ET]:
        """Return the entity with the given unique identifier.

        :param eid: Entity unique identifier.

        :return: Entity.
        """
        return cls.EDB.get(eid, None)

    @classmethod
    def get_by_component(
        cls: tp.Type[_ET],
        ctype: tp.Type[_CT],
    ) -> tp.List[_ET]:
        """Return the entities that have the given component type attached.

        :param ctype: Component type.

        :return: List of entities.
        """
        return [cls.get_by_id(eid=eid) for eid in cls.CDB.get(ctype, [])]

    @classmethod
    def register(
        cls: tp.Type[_ET],
        entity: _ET,
    ) -> None:
        """Register the entity in the entity database.

        :param entity: Entity to register.
        """
        if entity.id in cls.EDB:
            raise KeyError(f"Entity {entity.id} already registered.")
        cls.EDB[entity.id] = wr.proxy(entity, ft.partial(cls.unregister, eid=entity.id))

    @classmethod
    def unregister(
        cls: tp.Type[_ET],
        *args,
        eid: str,
    ) -> None:
        """Unregister the entity from the entity database.

        :param args: Positional arguments. Unused (dead weakref).
        :param eid: Entity unique identifier.
        """
        _ = args
        if eid in cls.EDB:
            cls.EDB.pop(eid, None)
        for _, eids in cls.CDB.items():
            if eid in eids:
                eids.remove(eid)


# -->> API <<---------------------------


# -->> Export <<------------------------
__all__ = [
    "Component",
    "Entity",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
