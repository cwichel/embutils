#!/usr/bin/python
# -*- coding: ascii -*-
"""
<TBD>

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import os
import sys

from .common import TPAny
from .path import Path

# -->> Tunables <<---------------------


# -->> Definitions <<------------------


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
    # Path Validation
    venv    = Path(venv)
    script  = Path.validate_file(path=venv / "Scripts/activate_this.py", must_exist=True)

    # Activation
    with script.open(mode="r", encoding="utf-8") as file:
        code = compile(file.read(), script, "exec")
        exec(code, dict(__file__=script))

    # Validation
    active = Path(os.environ["VIRTUAL_ENV"]) if ("VIRTUAL_ENV" in os.environ) else sys.executable
    if venv != active:
        raise EnvironmentError(f"Active environment doesn't match target: {venv} != {active}.")
