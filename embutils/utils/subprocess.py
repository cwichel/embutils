#!/usr/bin/python
# -*- coding: ascii -*-
"""
Subprocess execution utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import queue
import subprocess as sp
import sys
import time
import typing as tp

from .path import TPPath, path_validator
from .threading import SDK_TP, ThreadPool, SimpleThreadTask


# -->> Definitions <<------------------


# -->> API <<--------------------------
class StreamRedirect:
    """
    Stream redirect utility implementation.
    Allows to store and redirect a given stream.
    """
    def __init__(self,
                 name: str, stream_in: tp.IO[tp.AnyStr], stream_out: tp.IO[tp.AnyStr],
                 pool: ThreadPool = SDK_TP
                 ) -> None:
        """
        Class initialization.

        :param str name:                Stream redirection name (used for naming threads).
        :param IO[AnyStr] stream_in:    Input stream. Will be stored on buffer and redirected to output.
        :param IO[AnyStr] stream_out:   Output stream.
        :param ThreadPool pool:         Thread pool to be used by the stream redirection.
        """
        self._name  = name
        self._src   = stream_in
        self._out   = stream_out
        self._pool  = pool
        self._buff  = []
        self._queue = queue.Queue()
        self._ready = False
        self._start()

    @property
    def buffer(self) -> str:
        """
        Stream buffer.
        """
        return ''.join(self._buff)

    def wait_ready(self) -> None:
        """
        Waits until the stream is finished to continue.
        """
        while not self._ready:
            time.sleep(0.01)

    def _start(self) -> None:
        """
        Initializes the redirection read/write threads.
        """
        self._pool.enqueue(SimpleThreadTask(name=f"{self.__class__.__name__}_{self._name}_read", task=self._read))
        self._pool.enqueue(SimpleThreadTask(name=f"{self.__class__.__name__}_{self._name}_write", task=self._write))

    def _write(self) -> None:
        """
        Write every line into the output stream and buffer.
        """
        for line in iter(self._queue.get, None):
            self._out.write(line)

    def _read(self) -> None:
        """
        Parses and copies every line of the input stream.
        """
        for line in iter(self._src.readline, b''):
            line = line.decode()
            self._buff.append(line)
            self._queue.put(line)
        self._src.close()
        self._queue.put(None)
        self._ready = True


def execute(cmd: str, cwd: TPPath = None, log: TPPath = None, pipe: bool = True) -> sp.CompletedProcess:
    """
    Execute the given command as a subprocess.

    :param TPPath cmd:  Command to be executed.
    :param TPPath cwd:  Command working directory.
    :param TPPath log:  File to store the execution logs.
    :param bool pipe:   Enable pipe output to terminal.
    """
    # Check paths
    cwd = path_validator(path=cwd, allow_none=True, check_reachable=True)
    log = path_validator(path=log, allow_none=True, check_reachable=True)

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
            s_err.wait_ready()
            s_out.wait_ready()
            # Get buffers
            err = s_err.buffer
            out = s_out.buffer

        else:
            # Not piping needed...
            out, err = proc.communicate()
            out = '' if (out is None) else out.decode()
            err = '' if (err is None) else err.decode()

        # Retrieve execution result
        res = sp.CompletedProcess(args=proc.args, returncode=proc.returncode, stdout=out, stderr=err)

    # Store logs (if required)
    if log is not None:
        with log.open(mode='w') as file:
            file.write(f"Date: {time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime())}"
                       f"CWD : {cwd}\n"
                       f"CMD : {cmd}\n"
                       f"RET : {res.returncode}\n"
                       f"LOG : \n{out}\n{err}"
                       )

    # Return result
    return res
