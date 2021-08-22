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

from typing import Union


# -->> Definitions <<------------------


# -->> API <<--------------------------
def execute(cmd: str, ret: bool = False) -> Union[None, sp.CompletedProcess]:
    """
    Executed the command on the terminal.

    :param str cmd:  Command to be executed.
    :param bool ret: Returns the command output.
    """
    print(f'Executing:\n"{cmd}"\nOutput:')
    if ret:
        return sp.run(cmd, shell=True)
    sp.call(cmd, shell=True)
    return None
