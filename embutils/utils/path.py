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
class FileTypeError(OSError):
    """ File type is not the expected. """
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
        :raises FileNotFoundError:  Path cant be reached or doesnt exist.
        """
        # Check if input is none
        if path is None:
            if none_ok:
                return None
            raise ValueError("Validation failed: None is not accepted as path.")

        # Validate
        path = Path(path=path)
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
