#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Subprocess execution utilities.

:date:      2022
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

# Built-in
import io
import pathlib as pl
import subprocess as sp
import sys
import time
import typing as tp

# External
import attr

# App
from .path import validate_dir, validate_file


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
@attr.define
class _StreamPipe:
    """Subprocess piping helper class."""

    #: Target pipe name
    name: str = attr.field()
    #: Subprocess object
    proc: sp.Popen = attr.field()
    #: Auxiliary buffer
    buff: io.BytesIO = attr.field(factory=io.BytesIO)

    def __del__(self):
        """Ensure to close the auxiliary buffer on delete."""
        self.buff.close()

    def redirect(self) -> bool:
        """Redirect the stream until the process is ready."""
        line = getattr(self.proc, self.name).readline()
        if (line == b"") and (self.proc.poll() is not None):
            return True
        self.buff.write(line)
        getattr(sys, self.name).buffer.write(line)
        return False


def execute(
    args: tp.Union[str, list],
    cwd: tp.Union[str, pl.Path] = None,
    log: tp.Union[str, pl.Path] = None,
    shell: bool = False,
    capture: tp.Literal["NONE", "MIRROR", "FULL"] = "NONE",
) -> sp.CompletedProcess:
    """Execute a child program in a new process.

    :param tp.Union[str, list] args:    A string, or a sequence of program arguments
    :param tp.Union[str, pl.Path] cwd:  Sets the current directory before the child is executed
    :param tp.Union[str, pl.Path] log:  If provided, the command and outputs will be saved to a file
    :param bool shell:                  If true, the command will be executed through the shell
    :param bool capture:                Output capture method: FULL (app only), MIRROR (both), NONE (terminal only).

    :return: Subprocess execution results.
    :rtype: sp.CompletedProcess
    """
    # Prepare execution
    cwd = validate_dir(path=cwd, none_ok=True)
    log = validate_file(path=log, none_ok=True)
    pipe = sp.PIPE if (capture != "NONE") else None
    with sp.Popen(args, cwd=cwd, shell=shell, stdout=pipe, stderr=pipe) as proc:
        # Enable output capture
        if capture == "MIRROR":
            out = _StreamPipe(name="stdout", proc=proc)
            err = _StreamPipe(name="stderr", proc=proc)
            while not (out.redirect() and err.redirect()):
                continue
        # Wait for results
        proc.wait()
        ret = sp.CompletedProcess(args=proc.args, returncode=proc.returncode)
        if capture == "FULL":
            ret.stdout = proc.stdout.read()
            ret.stderr = proc.stderr.read()
        elif capture == "MIRROR":
            ret.stdout = out.buff.getvalue().decode()
            ret.stderr = err.buff.getvalue().decode()
    # Save execution log (if required)
    if log is not None:
        with log.open(mode="w", encoding="utf-8") as file:
            file.write(
                f"DATE: {time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime())}\n"
                f"CWD : {cwd}\n"
                f"CMD : {args}\n"
                f"RET : {ret.returncode}\n"
                f"OUT :\n{ret.stdout}\n"
                f"ERR :\n{ret.stderr}\n"
            )
    return ret


# -->> Export <<-----------------------
#: Filter to module imports
__all__ = [
    "execute",
]
