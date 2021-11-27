#!/usr/bin/python
# -*- coding: ascii -*-
"""
Path checking utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import pathlib as pl
import typing as tp

from .common import TPAny, TPPath


# -->> Definitions <<------------------


# -->> API <<--------------------------
class PathError(OSError):
    """ Path generic error. """
    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class PathExistenceError(OSError):
    """ Path dont exist. """
    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class PathReachableError(OSError):
    """ Path cant be reached. """
    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class Path(pl.Path):
    """
    Path class extensions.
    """
    def __new__(cls, path: TPAny = "") -> 'Path':
        """
        Extends the Path initialization supported types.

        :param TPAny path:      Value to be interpreted as path.

        :return: Path object.
        :rtype: pl.Path

        :raises TypeError:  Input type cant be converted to a path.
        """
        # Avoid not compatible types
        if not isinstance(path, TPPath.__constraints__):
            raise TypeError(f"Argument should be a compatible type ({TPPath.__constraints__}). {type(path)} is not supported.")

        # Convert
        try:
            obj = pl.Path(path)
        except TypeError:
            obj = pl.Path(path.decode(errors="ignore"))

        # Add extra functionalities
        setattr(obj.__class__, Path.reachable.__name__, Path.reachable)
        setattr(obj.__class__, Path.validate.__name__, staticmethod(Path.validate))
        setattr(obj.__class__, Path.validate_dir.__name__, staticmethod(Path.validate_dir))
        setattr(obj.__class__, Path.validate_file.__name__, staticmethod(Path.validate_file))
        return obj

    def reachable(self) -> bool:
        """
        Checks if the path is reachable.

        :returns: True if reachable, false otherwise.
        :rtype: bool
        """
        return self.exists() or self.parent.exists()

    @staticmethod
    def validate(
            path:       TPAny = None,
            none_ok:    bool = False,
            reachable:  bool = False,
            must_exist: bool = False
            ) -> tp.Optional['Path']:
        """
        Validates the provided input.

        :param TPAny path:          Path to be converted / validated.
        :param bool none_ok:        Allows None input.
        :param bool reachable:      Path must be reachable.
        :param bool must_exist:     Path must exist.

        :return: Verified path.
        :rtype: Path

        :raises TypeError:          Input type cant be converted to a path.
        :raises ValueError:         Provided path is not supported.
        :raises PathReachableError: Path cant be reached.
        :raises PathExistenceError: Path doesnt exist.
        """
        # Check if input is none
        if path is None:
            if none_ok:
                return None
            raise ValueError("Validation failed: None is not accepted as path.")

        # Validate
        path = Path(path=path)
        if reachable and not path.reachable():
            raise PathReachableError(f"Validation failed: {path} is not reachable.")
        if must_exist and not path.exists():
            raise PathExistenceError(f"Validation failed: {path} doesnt exist.")

        return path

    @staticmethod
    def validate_dir(
            path:       TPAny = None,
            none_ok:    bool = False,
            must_exist: bool = False,
            create: bool = False,
            ) -> tp.Optional['Path']:
        """
        Validate the directory path.

        :param TPAny path:          Path to be converted / validated.
        :param bool none_ok:        Allows None input.
        :param bool must_exist:     Path must exist.
        :param bool create:         create directory if doesn't exist.

        :return: Verified path.
        :rtype: Path

        :raises TypeError:          Input type cant be converted to a path.
        :raises ValueError:         Provided path is not supported.
        :raises PathError:          Path is not a directory.
        :raises PathReachableError: Path cant be reached.
        :raises PathExistenceError: Path doesnt exist.
        """
        # Validate base path
        path = Path.validate(path=path, none_ok=none_ok, reachable=True)
        if path is None:
            return None
        # Directory creation
        if create:
            path.mkdir(exist_ok=True)
        # Directory check specifics
        if path.exists() and not path.is_dir():
            raise PathError(f"Validation failed: {path} exists but is not a directory.")
        if must_exist and not path.exists():
            raise PathExistenceError(f"Validation failed: {path} doesnt exist.")
        return path

    @staticmethod
    def validate_file(
            path:       TPAny = None,
            none_ok:    bool = False,
            must_exist: bool = False,
            ) -> tp.Optional['Path']:
        """
        Validate the file path.

        :param TPAny path:          Path to be converted / validated.
        :param bool none_ok:        Allows None input.
        :param bool must_exist:     Path must exist.

        :return: Verified path.
        :rtype: Path

        :raises TypeError:          Input type cant be converted to a path.
        :raises ValueError:         Provided path is not supported.
        :raises PathError:          Path is not a file.
        :raises PathReachableError: Path cant be reached.
        :raises PathExistenceError: Path doesnt exist.
        """
        # Validate base path
        path = Path.validate(path=path, none_ok=none_ok, reachable=True, must_exist=must_exist)
        if path is None:
            return None
        # File check specifics
        if path.exists() and not path.is_file():
            raise PathError(f"Validation failed: {path} exists but is not a file.")
        return path
