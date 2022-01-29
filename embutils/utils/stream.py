#!/usr/bin/python
# -*- coding: ascii -*-
"""
Stream utilities.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""
# -------------------------------------

import contextlib as ctx
import io
import queue
import threading as th
import typing as tp

from .threading import SDK_TP, SimpleThreadTask


# -->> Tunables <<---------------------


# -->> Definitions <<------------------


# -->> API <<--------------------------
@ctx.contextmanager
def unclosable(file: io.IOBase):
    """
    Makes file unclosable during the context execution.
    """
    close = file.close
    file.close = lambda: None
    yield file
    file.close = close


class StreamRedirect:
    """
    Stream redirect utility implementation.
    Allows to store and redirect a given stream.
    """
    def __init__(self, name: str, stream_in: tp.IO[tp.AnyStr], stream_out: tp.IO[tp.AnyStr]) -> None:
        """
        Class initialization.

        :param str name:                Stream redirection name (used for naming threads).
        :param IO[AnyStr] stream_in:    Input stream. Will be stored on buffer and redirected to output.
        :param IO[AnyStr] stream_out:   Output stream.
        """
        # Configure redirection operation
        self._src   = stream_in
        self._out   = stream_out
        self._queue = queue.Queue()
        self._buff  = []
        self._ready = th.Event()
        # Start
        SDK_TP.enqueue(SimpleThreadTask(name=f"{self.__class__.__name__}_{name}_read", task=self._read))
        SDK_TP.enqueue(SimpleThreadTask(name=f"{self.__class__.__name__}_{name}_write", task=self._write))

    @property
    def buffer(self) -> str:
        """
        Stream buffer.
        """
        return "".join(self._buff)

    def join(self) -> None:
        """
        Waits until the stream is finished to continue.
        """
        self._ready.wait()

    def _write(self) -> None:
        """
        Writes every line into the output stream and buffer.
        """
        for line in iter(self._queue.get, None):
            self._buff.append(line)
            self._out.write(line)
        self._ready.set()

    def _read(self) -> None:
        """
        Parses and copies every line of the input stream.
        """
        for line in iter(self._src.readline, b""):
            self._queue.put(line.decode())
        self._queue.put(None)
        self._src.close()


# -->> Export <<-----------------------
__all__ = [
    "unclosable",
    "StreamRedirect",
    ]
