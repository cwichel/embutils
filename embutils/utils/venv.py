#!/usr/bin/python
# -*- coding: ascii -*-
"""
Virtual environment utilities.

:note:      Reference implementation.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import os
import site
import sys
import typing as tp

import attr

from .common import TPAny
from .path import Path

# -->> Tunables <<---------------------


# -->> Definitions <<------------------
@attr.s
class VENV:
    """
    Virtual environment info.
    """
    os_venv:    str = attr.ib(default="")
    sys_prefix: str = attr.ib(default=None)


#: History of activated environments
VENVS:  tp.List[VENV] = []


# -->> API <<--------------------------
def activate(venv: TPAny) -> None:
    """
    Activates the given virtual environment on the current run.

    :param TPAny venv:          Path to virtualenv folder.

    :raises TypeError:          Input type cant be converted to a path.
    :raises ValueError:         Provided path is not supported.
    :raises PathError:          Path is not a file.
    :raises FileNotFoundError:  Path cant be reached or doesnt exist.
    :raises EnvironmentError:   Virtualenv not active or it doesn't match target.
    """
    global VENVS

    # Path Validation
    venv = Path.validate_dir(path=venv, must_exist=True)
    find = list(venv.rglob(pattern="python.exe"))
    if not find:
        raise EnvironmentError(f"Python interpreter not found on virtual environment: {venv}")

    # Activate
    old_venv = VENV()

    # Get environment paths
    bins = venv / "Scripts"
    libs = venv / "Libs/site-packages"

    # Register environment
    if ("VIRTUAL_ENV" in os.environ) and (os.environ["VIRTUAL_ENV"] != ""):
        old_venv.os_venv = os.environ["VIRTUAL_ENV"]
    os.environ["VIRTUAL_ENV"] = f"{venv}"

    # Add binaries to path
    os.environ["PATH"] = f"{bins}{os.pathsep}{os.environ['PATH']}"

    # Add libraries to host python
    idx = len(sys.path)
    site.addsitedir(sitedir=libs)
    sys.path = sys.path[idx:] + sys.path[0:idx]

    # Update system prefix
    old_venv.sys_prefix = sys.prefix
    sys.prefix = f"{venv}"

    # Verify
    active = Path(sys.prefix)
    if venv != active:
        raise EnvironmentError(f"Active environment doesn't match target: {venv} != {active}.")
    VENVS.append(old_venv)


def deactivate() -> None:
    """
    Deactivates the current virtual environment.

    :note: This function can only deactivate environments activated during execution (stored in VENVS). 
    """
    global VENVS

    # Deactivate (only if we activated it)
    if VENVS:
        old_venv = VENVS.pop(-1)

        # Unregister environment
        os.environ["VIRTUAL_ENV"] = old_venv.os_venv

        # Remove binaries from path
        os.environ["PATH"] = f"{os.pathsep}".join(os.environ['PATH'].split(os.pathsep)[1:])

        # Remove libraries from host python
        sys.path = sys.path[1:]

        # Restore system prefix
        sys.prefix = old_venv.sys_prefix
