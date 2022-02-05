#!/usr/bin/python
# -*- coding: ascii -*-
"""
Subprocess execution utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import subprocess as sp
import sys
import time

from .common import TPPath
from .path import Path
from .stream import StreamRedirect


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
def execute(cmd: str, cwd: TPPath = None, log: TPPath = None, pipe: bool = True) -> sp.CompletedProcess:
    """
    Execute the given command as a subprocess.

    :param TPPath cmd:  Command to be executed.
    :param TPPath cwd:  Command working directory.
    :param TPPath log:  File to store the execution logs.
    :param bool pipe:   Enable pipe output to terminal.
    """
    # Check paths
    cwd = Path.validate_dir(path=cwd, none_ok=True)
    log = Path.validate_dir(path=log, none_ok=True)

    # Prepare
    with sp.Popen(cmd, cwd=cwd, shell=True, close_fds=True, stdout=sp.PIPE, stderr=sp.PIPE) as proc:
        # Execute
        if pipe:
            # Piping needed...
            # Print header
            print(f"Executing:\n{cmd}\nOutput:")
            # Set piping...
            s_err = StreamRedirect(name="stderr", stream_in=proc.stderr, stream_out=sys.stderr)
            s_out = StreamRedirect(name="stdout", stream_in=proc.stdout, stream_out=sys.stdout)
            # Wait for process and get data
            proc.wait()
            s_err.join()
            s_out.join()
            # Get buffers
            err = s_err.buffer
            out = s_out.buffer

        else:
            # Not piping needed...
            out, err = proc.communicate()
            out = "" if (out is None) else out.decode()
            err = "" if (err is None) else err.decode()

        # Retrieve execution result
        res = sp.CompletedProcess(args=proc.args, returncode=proc.returncode, stdout=out, stderr=err)

    # Store logs (if required)
    if log is not None:
        with log.open(mode="w", encoding="utf-8") as file:
            file.write(f"Date: {time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime())}\n"
                       f"CWD : {cwd}\n"
                       f"CMD : {cmd}\n"
                       f"RET : {res.returncode}\n"
                       f"LOG : \n{out}\n{err}"
                       )

    # Return result
    return res


# -->> Export <<-----------------------
__all__ = [
    "execute",
    ]
