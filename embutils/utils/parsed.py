#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Parsed object implementation.
In this context parse is converting data to/from text.

:date:      2022
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import binascii as ba
import enum
import functools as ft
import json
import typing as tp

import attr
import cattr
import yaml

from .common import ENCODE, TPAny, TPByte, TPPath, TPText
from .path import Path

# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
@attr.define
class ParseProtocolItem:
    """
    Parse protocol item.
    """
    #: Parsing method (string to dict...)
    parse:      tp.Callable[..., dict] = attr.field()
    #: Exporting method (dict to string...)
    export:     tp.Callable[..., str] = attr.field()
    #: Allowed file suffixes
    suffixes:   tp.List[str] = attr.field()


class ParseProtocol(enum.Enum):
    """
    Available parse protocol definitions.
    """
    JSON = ParseProtocolItem(
            parse=ft.partial(lambda s, **kwargs:     json.loads(s=s, **kwargs)),
            export=ft.partial(lambda obj, **kwargs:  json.dumps(obj=obj, **kwargs)),
            suffixes=[".json", ".js"]
            )
    YAML = ParseProtocolItem(
            parse=ft.partial(lambda s, **kwargs:     yaml.safe_load(stream=s)),
            export=ft.partial(lambda obj, **kwargs:  yaml.safe_dump(data=obj, **kwargs)),
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

    def dict(
            self, exc_none: bool = True, exc_empty: bool = True
            ) -> dict:
        """
        Generate a dictionary representation of the model.

        :param bool exc_none:       True to exclude None values.
        :param bool exc_empty:      True to exclude empty values: "", [], {}.

        :return: Object as dictionary.
        :rtype: dict
        """
        # Export, filter and return
        obj = self.CONVERTER.unstructure(obj=self)
        obj = self.obj_exclude(obj=obj, exc_none=exc_none, exc_empty=exc_empty)
        return obj

    def export(
            self, path: TPAny = None, protocol: ParseProtocol = None,
            exc_none: bool = True, exc_empty: bool = True,
            **kwargs) -> str:
        """
        Export the model to a text/file using a protocolized representation.

        :param TPAny path:              Path to store the exported object.
        :param ParseProtocol protocol:  Representation protocol.
        :param bool exc_none:           True to exclude None values.
        :param bool exc_empty:          True to exclude empty values: "", [], {}.

        :return: Object converted to protocol.
        :rtype: str
        """
        # Convert data
        protocol = protocol if protocol else self.PROTOCOL
        data = protocol.value.export(obj=self.dict(exc_none=exc_none, exc_empty=exc_empty), **kwargs)

        # Save to file if required
        path = Path.validate_file(path=path, none_ok=True, suffixes=protocol.value.suffixes)
        if path is not None:
            with path.open(mode="w", encoding=ENCODE) as file:
                file.write(data)

        # Return converted
        return data

    @classmethod
    def parse_obj(
            cls, obj: TPAny, exc_none: bool = True, exc_empty: bool = True
            ) -> 'ParseModel':
        """
        Parses the model from a dictionary-like object.

        :param TPAny obj:           Data to be parsed.
        :param bool exc_none:       True to exclude None values.
        :param bool exc_empty:      True to exclude empty values: "", [], {}.

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
        obj = cls.obj_exclude(obj=obj, exc_none=exc_none, exc_empty=exc_empty)

        # Apply conversion and return
        data = cls.CONVERTER.structure(obj=obj, cl=cls)
        return data

    @classmethod
    def parse_raw(
            cls, data: TPText, encoding: str = ENCODE, protocol: ParseProtocol = None,
            exc_none: bool = True, exc_empty: bool = True,
            **kwargs
            ) -> 'ParseModel':
        """
        Parses the model from raw data.

        :param TPText data:             Data to be parsed.
        :param str encoding:            Data encoding.
        :param ParseProtocol protocol:  Representation protocol.
        :param bool exc_none:       True to exclude None values.
        :param bool exc_empty:      True to exclude empty values: "", [], {}.

        :returns: Parsed object.
        :rtype: ParseModel

        :raises ValueError: Provided data has an unsupported type.
        """
        # Format, covert and parse
        protocol = protocol if protocol else cls.PROTOCOL
        data = data.decode(encoding=encoding) if not isinstance(data, str) else str(data)
        return cls.parse_obj(obj=protocol.value.parse(s=data, **kwargs), exc_none=exc_none, exc_empty=exc_empty)

    @classmethod
    def parse_file(
            cls, path: TPAny, encoding: str = ENCODE, protocol: ParseProtocol = None,
            exc_none: bool = True, exc_empty: bool = True,
            **kwargs
            ) -> 'ParseModel':
        """
        Parses the model from file.

        :param TPAny path:              Path to source file.
        :param str encoding:            Data encoding.
        :param ParseProtocol protocol:  Representation protocol.
        :param bool exc_none:           True to exclude None values.
        :param bool exc_empty:          True to exclude empty values: "", [], {}.

        :returns: Parsed object.
        :rtype: ParseModel

        :raises ValueError: Provided path has an unsupported type.
        """
        # Get protocol if not provided
        path = Path(path)
        if protocol is None:
            aux = [proto for proto in ParseProtocol if path.suffix in proto.value.suffixes]
            if not aux:
                raise ValueError(f"Unable to extract protocol from filename {path}")
            protocol = aux.pop(0)

        # Parse data
        path = Path.validate_file(path=path, must_exist=True, suffixes=protocol.value.suffixes)
        data = path.read_bytes()
        return cls.parse_raw(data=data, encoding=encoding, protocol=protocol, exc_none=exc_none, exc_empty=exc_empty, **kwargs)

    @classmethod
    def obj_exclude(
            cls, obj: dict, keys: tp.List[str] = None, values: tp.List[TPAny] = None,
            exc_none: bool = True, exc_empty: bool = True
            ) -> dict:
        """
        Dictionary exclusion utility.

        :note:
            - The exclusion is applied recursively only on dictionaries.
            - If a list or tuple is encountered the filter will be applied only on dictionary items.

        :param dict obj:            Object to be filtered.
        :param tp.List[str] keys:   List of keys to exclude.
        :param tp.List[str] values: List of values to exclude.
        :param bool exc_none:       True to exclude None values.
        :param bool exc_empty:      True to exclude empty values: "", [], {}.

        :returns: Filtered dictionary.
        :rtype: dict
        """
        tpl = tp.Union[list, tuple]

        # Check input
        if not any([keys, values, exc_none, exc_empty]):
            return obj

        # Prepare settings
        keys   = keys if (keys is not None) else []
        values = values if (values is not None) else []
        if exc_none:
            values.append(None)
        if exc_empty:
            values.extend(["", [], {}])

        def check(base: tp.Union[list, dict], ref: tp.Union[int, str], item: TPAny) -> None:
            """
            Check if the item is a list or dictionary. Check recursively if it's the case.
            """
            if isinstance(item, getattr(tpl, "__args__")):
                base[ref] = exc_list(src=item)
            elif isinstance(item, dict):
                base[ref] = exc_dict(src=item)

        def exc_list(src: tpl) -> tpl:
            """
            Check list items. Only process dictionaries.
            """
            aux = list(src)
            for idx, item in enumerate(aux):
                check(base=aux, ref=idx, item=item)
            return type(src)(aux)

        def exc_dict(src: dict) -> dict:
            """
            Check dictionaries. Remove selected keys or entries with given value.
            """
            _ = [src.pop(key) for key in keys]
            tmp = src.copy()
            for key, item in tmp.items():
                check(base=src, ref=key, item=item)
                if src[key] in values:
                    src.pop(key)
            return src

        return exc_dict(src=obj)


# Converter adapters
ParseModel.CONVERTER.register_structure_hook(TPByte,    func=lambda x, _: bytearray(ba.a2b_base64(x)))
ParseModel.CONVERTER.register_structure_hook(TPPath,    func=lambda x, _: Path(x))
ParseModel.CONVERTER.register_structure_hook(TPText,    func=lambda x, _: str(x))
ParseModel.CONVERTER.register_unstructure_hook(TPByte,  func=lambda x: ba.b2a_base64(x).decode(encoding=ENCODE) if x else None)
ParseModel.CONVERTER.register_unstructure_hook(TPPath,  func=lambda x: str(x) if x else None)
ParseModel.CONVERTER.register_unstructure_hook(TPText,  func=lambda x: str(x) if x else None)


# -->> Export <<-----------------------
__all__ = [
    "ParseProtocolItem",
    "ParseProtocol",
    "ParseModel",
    ]
