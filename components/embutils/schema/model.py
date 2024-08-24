#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Base schema model implementation.

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

# External
import pydantic as pdt


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
_MT = tp.TypeVar("_MT", bound="BaseModel")
"""Model type variable."""

_EXS = tp.Union[None, tp.Set[int], tp.Set[str], tp.Dict[int, tp.Any], tp.Dict[str, tp.Any]]
"""Exclude Set type. Check for IncEx on pydantic.main for more info."""


class BaseModel(pdt.BaseModel):
    """Generic schema model class with additional utility methods."""

    __slots__ = ("__weakref__",)
    model_config = {
        "arbitrary_types_allowed": True,
    }

    def __init__(
        self,
        **kwargs,
    ) -> None:
        """Initialize the model.

        :param kwargs: Initialization arguments.
        """
        self._pre_init(**kwargs)
        super().__init__(**kwargs)
        self._post_init(**kwargs)

    def model_dump(
        self,
        *,
        mode: tp.Union[str, tp.Literal["json", "python"]] = "python",
        include: _EXS = None,
        exclude: _EXS = None,
        context: tp.Any | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: tp.Union[bool, tp.Literal["none", "warn", "error"]] = True,
        serialize_as_any: bool = False,
    ) -> tp.Dict[str, tp.Any]:
        # Docstring inherited from BaseModel.
        return self._export(
            obj=self.__pydantic_serializer__.to_python(
                self,
                mode=mode,
                by_alias=by_alias,
                include=include,
                exclude=exclude,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
            )
        )

    def _export(
        self,
        obj: tp.Dict[str, tp.Any],
    ) -> tp.Dict[str, tp.Any]:
        """Utility function fo edit the instance exported object before return.

        :param obj: Object to export.

        :return: Exported object.
        """
        _ = self
        return obj

    def _pre_init(
        self,
        **kwargs,
    ) -> None:
        """Pre-initialization hook.

        :param kwargs: Initialization arguments.
        """

    def _post_init(
        self,
        **kwargs,
    ) -> None:
        """Post-initialization hook.

        :param kwargs: Initialization arguments.
        """

    @classmethod
    def get_field_names(
        cls: tp.Type[_MT],
        use_alias: bool = False,
        exclude_no_init: bool = False,
        include_excluded: bool = True,
    ) -> tp.List[str]:
        """Get the model field names.

        :param use_alias: Whether to return the field names by alias or not.
        :param exclude_no_init: Whether to exclude fields that are not initialized or not.
        :param include_excluded: Whether to include excluded fields or not.

        :return: List of field names.
        """
        fields = []
        for field, item in cls.model_fields.items():
            key = (item.alias or field) if use_alias else field
            if isinstance(item.exclude, bool) and item.exclude and not include_excluded:
                continue
            if isinstance(item.init_var, bool) and not item.init_var and exclude_no_init:
                continue
            fields.append(key)
        return fields

    @classmethod
    def parse(
        cls: tp.Type[_MT],
        obj: tp.Union[list, tuple, dict, _MT],
    ) -> _MT:
        """Create a model instance from an object.

        :param obj: Object to create the model from.

        :return: Model instance.
        """
        if isinstance(obj, cls):
            return obj.model_copy()
        if not isinstance(obj, dict):
            obj = {key: value for key, value in zip(cls.get_field_names(exclude_no_init=True), obj)}
        return cls(**obj)


# -->> API <<---------------------------


# -->> Export <<------------------------
__all__ = [
    "BaseModel",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
