#!/usr/bin/python
# -*- coding: ascii -*-
"""
Path handling utilities.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Union


def path_format(path: Union[str, Path], root: Union[str, Path] = '') -> Path:
    """Formats the given path. If the input correspond to a
    relative path and the root is set then it'll return an
    append between root and path.

    Args:
        path (Union[str, Path]): Path to be formatted.
        root (Union[str, Path]): Base path used to generate the absolute paths.

    Return:
        Path: Formatted path.
        root
    """
    path = Path(path)
    root = None if (root == '') else Path(root)

    if not path.is_absolute() and root:
        return Path(os.path.abspath(root / path))
    else:
        return path


def path_check_dir(path: Union[str, Path], mk_dir: bool = False) -> Tuple[bool, str]:
    """Check if the path is a directory.

    Args:
        path (Path): Path to the directory to be checked.
        mk_dir (bool): If true the folder will be created.

    Returns:
        Tuple[bool, str]: Status and message. True if success, false otherwise.
    """
    path = Path(path)
    if path.exists():
        test = path.is_dir()
        msg = 'Folder found!' if test else 'The path exists but is a file!'
        return test, (msg + ' \'{}\'').format(path)
    else:
        if mk_dir and path.parent.exists():
            path.mkdir()
            msg = 'Folder created! \'{}\''
            return True, msg.format(path)
        else:
            msg = 'The specified path doesnt exist! \'{}\''
            return False, msg.format(path)


def path_check_file(path: Union[str, Path], required: bool = False) -> Tuple[bool, str]:
    """Check if the path is a file.

    Args:
        path (Path): Path to the file to be checked.
        required (bool): If true the existence of the file will be required.

    Returns:
        Tuple[bool, str]: Status and message. True if success, false otherwise.
    """
    path = Path(path)
    if path.exists():
        test = path.is_file()
        msg = 'File found!' if test else 'The path exist but is a folder!'
        return test, (msg + ' \'{}\'').format(path)
    else:
        if not required and path.parent.exists():
            msg = 'Path is available but the file is not created! \'{}\''.format(path)
            return True, msg.format(path)
        else:
            msg = 'File doesnt exist! \'{}\''
            return False, msg.format(path)


def path_filter(path: Union[str, Path], pattern: str) -> List[Path]:
    """Return all the elements that match with the pattern
    in the given directory path.

    Args:
        path (Path): Base path. The algorithm will filter the elements here.
        pattern (str): Path/file pattern.

    Returns:
        List[Path]: Paths found.
    """
    path = Path(path)

    # Check that the given path is a folder
    check = path_check_dir(path=path, mk_dir=False)
    if not check:
        return []

    # Return the matching list
    files = []
    for item in path.iterdir():
        match = re.findall(pattern=pattern, string=item.as_posix(), flags=re.I)
        if match:
            files.append(item)
    return files
