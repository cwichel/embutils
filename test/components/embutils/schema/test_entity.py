#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Entity-Component System (ECS) implementation test suite.

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
import pydantic as pdt
from embutils.schema import Component, Entity


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
class Point(Component):
    """2D Point."""

    x: int = pdt.Field(default=0)
    y: int = pdt.Field(default=0)


class Area(Point):
    """2D Area."""

    width: int = pdt.Field(default=0)
    height: int = pdt.Field(default=0)


class AreaRenderer(Component):
    """Component used to render an area."""

    area: str = pdt.Field()

    def draw(
        self,
    ) -> None:
        area = self.entity[self.area]
        print(f"Drawing at ({area.x}, {area.y}) with size ({area.width}, {area.height}).")


class EntityTestSuite(ut.TestCase):
    def setUp(
        self,
    ) -> None:
        """Set up the test suite."""
        self.entity = Entity()
        self.entity.attach(component=Area(x=0, y=23, width=10, height=10), alias="rect")
        self.entity.attach(component=AreaRenderer(area="rect"), alias="render")

    def test_getEntity(
        self,
    ) -> None:
        """Test entity retrieval."""
        self.assertEqual(self.entity.id, Entity.get_by_id(eid=self.entity.id).id)

    def test_getComponent(
        self,
    ) -> None:
        """Test component retrieval."""
        self.assertEqual(id(self.entity.rect), id(self.entity["rect"]))
        self.assertEqual(id(self.entity.rect), id(self.entity["Area"]))
        self.assertEqual(id(self.entity.rect), id(self.entity.Area))
        self.assertIsInstance(self.entity.rect, Area)

    def test_attachDetachComponents(
        self,
    ) -> None:
        """Test component attachment and detachment."""
        # Where the components attached?
        self.assertEqual(len(self.entity), 2)
        self.assertTrue(self.entity.has(Area))
        self.assertTrue(self.entity.has(AreaRenderer))

        # Can we detach them by tag?
        self.entity.detach("rect")
        self.assertEqual(len(self.entity), 1)
        self.assertFalse(self.entity.has(Area))

        # Can we detach all?
        self.setUp()
        self.entity.detach()
        self.assertEqual(len(self.entity), 0)
        self.assertFalse(self.entity.has(Area))
        self.assertFalse(self.entity.has(AreaRenderer))

        # Can we attach a component with a conflicting tag?
        self.entity.detach()
        self.assertRaises(KeyError, self.entity.attach, component=Area(x=0, y=23, width=10, height=10), alias="id")
        self.entity.attach(component=Area(x=0, y=23, width=10, height=10), alias="rect")
        self.assertRaises(KeyError, self.entity.attach, component=Area(x=0, y=23, width=10, height=10), alias="rect")

    def test_registerUnregisterOverride(
        self,
    ) -> None:
        """Test override registration and unregistration."""
        # Can we register an override?
        self.assertIsNone(getattr(self.entity, "test_method", None))
        self.entity.register_override(source="test1", override={"test_method": lambda: "test1"})
        self.assertIsNotNone(getattr(self.entity, "test_method", None))
        self.assertEqual(self.entity.test_method(), "test1")

        # Can we override an override?
        self.entity.register_override(source="test2", override={"test_method": lambda: "test2"})
        self.assertEqual(self.entity.test_method(), "test2")

        # Can we unregister an override?
        self.entity.unregister_override(source="test2")
        self.assertEqual(self.entity.test_method(), "test1")
        self.entity.unregister_override(source="test1")
        self.assertIsNone(getattr(self.entity, "test_method", None))

        # Can we override a protected item (attribute, components)?
        self.assertRaises(AttributeError, self.entity.register_override, source="test", override={"id": lambda: print("test")})
        self.assertRaises(AttributeError, self.entity.register_override, source="test", override={"render": lambda: print("test")})
        self.assertRaises(TypeError, self.entity.register_override, source="test", override={"new_var": 0})


# -->> API <<---------------------------


# -->> Export <<------------------------
# Meant as a script, not a module. No items will be exported.


# -->> Execute <<-----------------------
if __name__ == "__main__":
    ut.main()
