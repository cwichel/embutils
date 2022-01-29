#!/usr/bin/python
# -*- coding: ascii -*-
"""
Path checking utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import pathlib as pl
import typing as tp

from .common import TPAny, TPByte, TPPath


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
class FileTypeError(OSError):
    """
    File type is not the expected.
    """


class Path(pl.Path):
    """
    Path class extensions.
    """
    def __new__(cls, *args, **kwargs) -> 'Path':
        """
        Extends the Path initialization to new supported types.

        :return: Path object.
        :rtype: pl.Path

        :raises TypeError:  Input type cant be converted to a path.
        """
        tp_byte = getattr(TPByte, "__constraints__")
        tp_path = getattr(TPPath, "__constraints__")

        # Avoid not compatible types
        path  = []
        for item in args:
            # Check type
            if not isinstance(item, tp_path):
                raise TypeError(f"Argument should be a compatible type ({tp_path}). {type(item)} is not supported.")
            # Convert
            if isinstance(item, tp_byte):
                path.append(bytes(item).decode(errors="ignore"))
            else:
                path.append(str(item))

        # Generate object and add extra functionalities
        obj = pl.Path(*tuple(path))
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
        :raises FileNotFoundError:  Path cant be reached or doesnt exist.
        """
        # Check if input is none
        if path is None:
            if none_ok:
                return None
            raise ValueError("Validation failed: None is not accepted as path.")

        # Validate
        path = Path(path)
        if reachable and not path.reachable():
            raise FileNotFoundError(f"Validation failed: {path} is not reachable.")
        if must_exist and not path.exists():
            raise FileNotFoundError(f"Validation failed: {path} doesnt exist.")

        return path

    @staticmethod
    def validate_dir(
            path:       TPAny = None,
            none_ok:    bool = False,
            must_exist: bool = False,
            create:     bool = False,
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
        :raises FileNotFoundError:  Path cant be reached or doesnt exist.
        """
        # Validate base path
        path = Path.validate(path=path, none_ok=none_ok, reachable=True)
        if path is None:
            return None

        # Create
        if create and not path.exists():
            path.mkdir()

        # Validate
        if must_exist and not path.exists():
            raise FileNotFoundError(f"Validation failed: {path} doesnt exist.")
        if path.exists() and not path.is_dir():
            raise FileTypeError(f"Validation failed: {path} exists but is not a directory.")

        return path

    @staticmethod
    def validate_file(
            path:       TPAny = None,
            none_ok:    bool = False,
            must_exist: bool = False,
            default:    str = None
            ) -> tp.Optional['Path']:
        """
        Validate the file path.

        :param TPAny path:          Path to be converted / validated.
        :param bool none_ok:        Allows None input.
        :param bool must_exist:     Path must exist.
        :param str default:         Filename to be used when the input is a directory.

        :return: Verified path.
        :rtype: Path

        :raises TypeError:          Input type cant be converted to a path.
        :raises ValueError:         Provided path is not supported.
        :raises PathError:          Path is not a file.
        :raises FileNotFoundError:  Path cant be reached or doesnt exist.
        """
        # Validate base path
        path = Path.validate(path=path, none_ok=none_ok, reachable=True)
        if path is None:
            return None

        # Default
        if default and path.exists() and path.is_dir():
            path = path / default

        # Validate
        if must_exist and not path.exists():
            raise FileNotFoundError(f"Validation failed: {path} doesnt exist.")
        if path.exists() and not path.is_file():
            raise FileTypeError(f"Validation failed: {path} exists but is not a file.")

        return path


# -->> Export <<-----------------------
__all__ = [
    "FileTypeError",
    "Path",
    ]
