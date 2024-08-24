#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Subprocess execution utilities.

:date:      2024
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# --------------------------------------
__author__ = "Christian Wiche"
__version__ = "ALPHA"
# --------------------------------------

# Built-in
import dataclasses as dc
import io
import os
import pathlib as pl
import subprocess as sp
import sys
import time
import typing as tp


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
@dc.dataclass
class StreamRedirect:
    """Subprocess stream piping helper class.

    :param stream: Target pipe name.
    :param process: Subprocess object.
    :param enabled: Enable pipe.
    """

    stream: tp.Literal["stdout", "stderr"] = dc.field()
    process: sp.Popen = dc.field()
    enabled: bool = dc.field(default=True)
    buffer: io.BytesIO = dc.field(init=False, default_factory=io.BytesIO)

    def __del__(
        self,
    ) -> None:
        """Ensure to close the auxiliary buffer on delete."""
        self.buffer.close()

    def redirect(
        self,
    ) -> bool:
        """Redirect the pipe until the process is ready."""
        line = getattr(self.process, self.stream).readline()
        # Process ready
        if not line and self.process.poll() is not None:
            return True
        # Redirect
        self.buffer.write(line)
        if self.enabled:
            getattr(sys, self.stream).write(line.decode())
        return False


# -->> API <<---------------------------
def execute(
    cmd: tp.Union[str, tp.List[str]],
    cwd: tp.Optional[tp.Union[str, pl.Path]] = None,
    shell: bool = False,
    capture: tp.Literal["full", "mirror", "none"] = "full",
    logfile: tp.Optional[tp.Union[str, pl.Path]] = None,
) -> sp.CompletedProcess:
    """Execute a subprocess.

    :param cmd: Command to execute.
    :param cwd: Working directory.
    :param shell: Shell mode.
    :param capture: Capture mode. Modes:
        - "full": Capture all. No console output.
        - "mirror": Capture and console output.
        - "none": No capture. Console output.
    :param logfile: Optional. Log file path.
    :return: Completed process object.
    """
    pipe_console = capture == "mirror"
    pipe_capture = capture != "none"
    pipe_mode = sp.PIPE if pipe_capture else None
    # Start process
    with sp.Popen(cmd, cwd=cwd, shell=shell, stdout=pipe_mode, stderr=pipe_mode) as process:
        # Enable pipes and start
        if pipe_capture:
            stderr = StreamRedirect(stream="stderr", process=process, enabled=pipe_console)
            stdout = StreamRedirect(stream="stdout", process=process, enabled=pipe_console)
            while not (stdout.redirect() and stderr.redirect()):
                continue
        process.wait()
    # Prepare return
    result = sp.CompletedProcess(args=process.args, returncode=process.returncode)
    if pipe_capture:
        result.stdout = stdout.buffer.getvalue().decode()
        result.stderr = stderr.buffer.getvalue().decode()
    # Log to file
    if logfile:
        logfile = pl.Path(logfile)
        if not logfile.parent.exists():
            logfile.parent.mkdir(parents=True, exist_ok=True)
        with logfile.open(mode="w") as file:
            file.write(f"DATE: {time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime())}\n")
            file.write(f"CMD : {cmd}\n")
            file.write(f"CWD : {pl.Path(cwd) if cwd else os.getcwd()}\n")
            file.write(f"RET : {result.returncode}\n")
            file.write(f"OUT :\n{result.stdout}\n")
            file.write(f"ERR :\n{result.stderr}\n")
    return result


# -->> Export <<------------------------
__all__ = [
    "execute",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
