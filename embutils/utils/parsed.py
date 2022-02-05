#!/usr/bin/python
# -*- coding: ascii -*-
"""
Parsed object implementation.
In this context parse is converting data to/from text.

:date:      2022
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import enum
import functools as ft
import json
import typing as tp

import attr
import cattr
import yaml

from .common import ENCODE, TPAny, TPPath, TPText
from .path import Path

# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
@attr.s
class ParseProtocolItem:
    """
    Parse protocol item.
    """
    #: Parsing method
    parse:      tp.Callable[[str, ...], dict] = attr.ib()
    #: Exporting method
    export:     tp.Callable[[dict, ...], str] = attr.ib()
    #: Allowed file suffixes
    suffixes:   tp.List[str] = attr.ib()


class ParseProtocol(enum.Enum):
    """
    Available parse protocol definitions.
    """
    JSON = ParseProtocolItem(
            parse=ft.partial(lambda s, *args, **kwargs:     json.loads(s=s, *args, **kwargs)),
            export=ft.partial(lambda obj, *args, **kwargs:  json.dumps(obj=obj, *args, **kwargs)),
            suffixes=[".json", ".js"]
            )
    YAML = ParseProtocolItem(
            parse=ft.partial(lambda s, *args, **kwargs:     yaml.safe_load(stream=s)),
            export=ft.partial(lambda obj, *args, **kwargs:  yaml.safe_dump(data=obj, *args, **kwargs)),
            suffixes=[".yaml", ".yml"]
            )


class ParseModel:
    """
    Parseable object base implementation.
    This class gives parsing capabilities for an object.
    """
    #: Default parse protocol
    PROTOCOL  = ParseProtocol.YAML
    #: Class to object converter
    CONVERTER = cattr.Converter(unstruct_strat=cattr.UnstructureStrategy.AS_DICT)

    def dict(self, exc_none: bool = True) -> dict:
        """
        Generate a dictionary representation of the model.

        :param bool exc_none:       True to exclude None values.

        :return: Object as dictionary.
        :rtype: dict
        """
        # Export, filter and return
        obj = self.CONVERTER.unstructure(obj=self)
        obj = self.obj_exclude(obj=obj, exc_none=exc_none)
        return obj

    def export(
            self, path: TPPath = None, protocol: ParseProtocol = PROTOCOL, exc_none: bool = True,
            *args, **kwargs
            ) -> str:
        """
        Export the model to a text/file using a protocolized representation.

        :param TPPath path:             Path to store the exported object.
        :param ParseProtocol protocol:  Representation protocol.
        :param bool exc_none:           True to exclude None values.

        :return: Object converted to protocol.
        :rtype: str
        """
        # Convert data
        data = protocol.value.export(obj=self.dict(exc_none=exc_none), *args, **kwargs)
        # Save to file if required
        path = Path.validate_file(path=path, none_ok=True, suffixes=protocol.value.suffixes)
        if path is not None:
            with path.open(mode="r", encoding=ENCODE) as file:
                file.write(data)
        # Return converted
        return data

    @classmethod
    def parse_obj(cls, obj: TPAny, exc_none: bool = True) -> 'ParseModel':
        """
        Parses the model from a dictionary-like object.

        :param TPAny obj:       Data to be parsed.
        :param bool exc_none:   True to exclude None values.

        :returns: Parsed object.
        :rtype: ParseModel

        :raises ValueError: Provided object cant be converted to dictionary.
        """
        # Format and filter input
        if not isinstance(obj, dict):
            try:
                obj = dict(obj)
            except (TypeError, ValueError) as ex:
                raise ValueError(f"{cls.__name__} expected dict, not {obj.__class__.__name__}") from ex
        obj = cls.obj_exclude(obj=obj, exc_none=exc_none)
        # Apply conversion and return
        data = cls.CONVERTER.structure(obj=obj, cl=cls)
        return data

    @classmethod
    def parse_raw(
            cls, data: TPText, encoding: str = ENCODE, protocol: ParseProtocol = PROTOCOL, exc_none: bool = True,
            *args, **kwargs
            ) -> 'ParseModel':
        """
        Parses the model from raw data.

        :param TPText data:             Data to be parsed.
        :param str encoding:            Data encoding.
        :param ParseProtocol protocol:  Representation protocol.
        :param bool exc_none:           True to exclude None values.

        :returns: Parsed object.
        :rtype: ParseModel

        :raises ValueError: Provided data has an unsupported type.
        """
        # Check input
        if not isinstance(data, getattr(TPText, "__args__")):
            raise ValueError(f"{cls.__name__} expected {getattr(TPText, '__args__')}, not {data.__class__.__name__}")
        # Format
        data = data.decode(encoding=encoding) if not isinstance(data, str) else data
        protocol = protocol or cls.PROTOCOL
        # Conversion and parse
        return cls.parse_obj(obj=protocol.value.parse(s=data, *args, **kwargs), exc_none=exc_none)

    @classmethod
    def parse_file(
            cls, path: TPPath, encoding: str = ENCODE, protocol: ParseProtocol = None, exc_none: bool = True,
            *args, **kwargs
            ) -> 'ParseModel':
        """
        Parses the model from file.

        :param TPPath path:             Path to source file.
        :param str encoding:            Data encoding.
        :param ParseProtocol protocol:  Representation protocol.
        :param bool exc_none:           True to exclude None values.

        :returns: Parsed object.
        :rtype: ParseModel

        :raises ValueError: Provided path has an unsupported type.
        """
        # Check input
        if not isinstance(path, getattr(TPPath, "__args__")):
            raise ValueError(f"{cls.__name__} expected {getattr(TPPath, '__args__')}, not {path.__class__.__name__}")
        # Process
        path = Path.validate_file(path=path, must_exist=True, suffixes=protocol.value.suffixes)
        data = path.read_bytes()
        if protocol is None:
            for item in ParseProtocol:
                if path.suffix in item.value.suffix:
                    protocol = item
                    break
        # Parse data
        return cls.parse_raw(data=data, encoding=encoding, protocol=protocol, exc_none=exc_none, *args, **kwargs)

    @classmethod
    def obj_exclude(cls, obj: dict, keys: tp.List[str] = None, values: tp.List[TPAny] = None, exc_none: bool = True) -> dict:
        """
        Dictionary exclusion utility.

        :note: The exclusion is applied recursively.

        :param dict obj:            Object to be filtered.
        :param tp.List[str] keys:   List of keys to exclude.
        :param tp.List[str] values: List of values to exclude.
        :param bool exc_none:       True to exclude None values.

        :returns: Filtered dictionary.
        :rtype: dict
        """
        # Check input
        if not exc_none and not keys and not values:
            return obj
        # Prepare input
        keys   = keys if (keys is not None) else []
        values = values if (values is not None) else []
        if exc_none:
            values.append(None)
        # Filter
        tmp = obj.copy()
        for key, item in tmp.items():
            # Filter key
            if key in keys:
                del obj[key]
                continue
            # Filter internal dictionaries and lists
            if isinstance(item, (list, tuple)):
                obj[key] = type(item)(filter(lambda x: x not in values, item))
            elif isinstance(item, dict):
                obj[key] = cls.obj_exclude(obj=item, keys=keys, values=values)
            # Filter values
            if item in values:
                del obj[key]
        return obj


# -->> Export <<-----------------------
__all__ = [
    "ParseProtocolItem",
    "ParseProtocol",
    "ParseModel",
    ]
