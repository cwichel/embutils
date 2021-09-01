#!/usr/bin/python
# -*- coding: ascii -*-
"""
Subprocess execution utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import subprocess as sp

from typing import Optional


# -->> Definitions <<------------------


# -->> API <<--------------------------
def execute(cmd: str, ret: bool = False) -> Optional[sp.CompletedProcess]:
    """
    Execute the given command as a subprocess.

    :param str cmd:  Command to be executed.
    :param bool ret: True if the command return is required, false otherwise.
    """
    print(f'Executing:\n"{cmd}"\nOutput:')
    if ret:
        return sp.run(cmd, shell=True)
    sp.call(cmd, shell=True)
    return None
