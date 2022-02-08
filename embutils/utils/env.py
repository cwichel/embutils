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
# -------------------------------------

import contextlib as ctx
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
@ctx.contextmanager
def env(*remove, **update) -> tp.Iterator[None]:
    """
    Temporarily updates the "os.environ" dictionary in-place.

    The "os.environ" dictionary is updated in-place so that the modification
    is sure to work in all situations.

    :param remove: Environment variables to remove.
    :param update: Dictionary of environment variables and values to add/update.
    """
    # Get variables
    cwe     = os.environ
    update  = update or {}
    remove  = remove or []

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(cwe.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: cwe[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in cwe)

    # Execute
    try:
        # Update and execute
        cwe.update(update)
        _ = [cwe.pop(k, None) for k in remove]
        yield
    finally:
        # Restore
        cwe.update(update_after)
        _ = [cwe.pop(k) for k in remove_after]


@ctx.contextmanager
def venv(path: TPAny) -> tp.Iterator[None]:
    """
    Temporarily activates the given virtual environment.

    :param TPAny path: Path to virtualenv folder.
    """
    try:
        venv_activate(path=path)
        yield
    finally:
        venv_deactivate()


def venv_activate(path: TPAny) -> None:
    """
    Activates the given virtual environment on the current run.

    :param TPAny path: Path to virtualenv folder.

    :raises EnvironmentError: Virtualenv is not found or it doesn't match target.
    """
    # Path Validation
    path = Path.validate_dir(path=path, must_exist=True)
    if not list(path.rglob(pattern="python.exe")):
        raise EnvironmentError(f"Python interpreter not found on virtual environment: {path}")

    # Add current environment to env list
    VENVS.append(VENV(os_venv=os.environ.get("VIRTUAL_ENV", ""), sys_prefix=sys.prefix))

    # Register and include binaries
    os.environ["VIRTUAL_ENV"] = f"{path}"
    os.environ["PATH"]        = f"{(path / 'Scripts')}{os.pathsep}{os.environ['PATH']}"

    # Add python libraries to host
    idx = len(sys.path)
    site.addsitedir(sitedir=(path / "Libs/site-packages"))
    sys.path = sys.path[idx:] + sys.path[0:idx]

    # Update system prefix
    sys.prefix = f"{path}"

    # Verify
    active = Path(sys.prefix)
    if path != active:
        VENVS.pop(-1)
        raise EnvironmentError(f"Active environment doesn't match target: {path} != {active}.")


def venv_deactivate() -> None:
    """
    Deactivates the current virtual environment.

    :note: This function can only deactivate environments activated during execution (stored in VENVS).
    """
    # Deactivate (only if we activated it)
    if VENVS:
        old_venv = VENVS.pop(-1)

        # Unregister environment
        os.environ["VIRTUAL_ENV"] = old_venv.os_venv

        # Remove binaries and libraries
        os.environ["PATH"] = f"{os.pathsep}".join(os.environ['PATH'].split(os.pathsep)[1:])
        sys.path = sys.path[1:]

        # Restore system prefix
        sys.prefix = old_venv.sys_prefix


# -->> Export <<-----------------------
__all__ = [
    "VENV",
    "VENVS",
    "env",
    "venv",
    "venv_activate",
    "venv_deactivate",
    ]
