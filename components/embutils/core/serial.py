#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------
"""Serial utilities.

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
import typing as tp

# External
import serial as ser
import serial.tools.list_ports as ser_tlp
import serial.tools.list_ports_common as ser_tlpc


# -->> Tunables <<----------------------


# -->> Definitions <<-------------------
_ST = tp.TypeVar("_ST", bound="Parent")  # noqa: F821
"""Serial type variable."""


class SerialDevice:
    """Serial device wrapper.

    Use this class to implement utilities for serial devices.

    This class can be used for both "normal" serial objects and URL-based generators:
    - For normal use, pass a serial object to the constructor.
    - For URL-based use, pass the URL to the constructor and use the from_url() method.

    """

    def __init__(
        self,
        serial: tp.Optional[ser.SerialBase] = None,
    ) -> None:
        """Initialize the serial device."""
        self._info: tp.Optional[ser_tlpc.ListPortInfo] = None
        self._io: tp.Optional[ser.SerialBase] = None
        self.io = serial

    @property
    def info(
        self,
    ) -> tp.Optional[ser_tlpc.ListPortInfo]:
        """Get the device information.

        :return: Device information.
        """
        if self._info is None:
            self.update_info()
        return self._info

    @property
    def io(
        self,
    ) -> ser.SerialBase:
        """Get the device I/O object.

        :return: Device I/O object.
        """
        return self._io

    @io.setter
    def io(
        self,
        value: ser.SerialBase,
    ) -> None:
        """Set the device I/O object.

        :param value: Device I/O object.
        """
        self.disconnect()
        self._io = value
        self.update_info()

    @property
    def in_waiting(
        self,
    ) -> int:
        """Get the number of bytes in the input buffer.

        :return: Number of bytes in the input buffer.
        """
        if not (isinstance(self._io, ser.SerialBase) and self.io.is_open):
            return 0
        return getattr(self._io, "in_waiting", 0)

    def clear(
        self,
    ) -> None:
        """Clear the device buffers."""
        if isinstance(self._io, ser.SerialBase) and self._io.is_open:
            getattr(self._io, "reset_input_buffer", lambda: None)()
            getattr(self._io, "reset_output_buffer", lambda: None)()

    def connect(
        self,
    ) -> None:
        """Connect to the device."""
        if isinstance(self._io, ser.SerialBase) and not self._io.is_open:
            getattr(self._io, "open", lambda: None)()

    def disconnect(
        self,
    ) -> None:
        """Disconnect from the device."""
        if isinstance(self._io, ser.SerialBase):
            self.clear()
            self.io.close()

    def update_info(
        self,
    ) -> None:
        """Update the device information."""
        self._info = None
        if isinstance(self._io, ser.SerialBase) and self._io.port:
            find = list(ser_tlp.grep(regexp=self._io.port))
            self._info = find[0] if find else None

    # noinspection PyTypeChecker
    @staticmethod
    def get_ports(
        regexp: tp.Optional[str] = None,
    ) -> tp.List[ser_tlpc.ListPortInfo]:
        """Get the list of available ports.

        :param regexp: Regular expression to filter the list of ports.

        :return: List of available ports.
        """
        return list(ser_tlp.grep(regexp=regexp) if regexp else ser_tlp.comports())

    @classmethod
    def from_url(
        cls: tp.Type[_ST],
        url: str,
        *args,
        **kwargs,
    ) -> _ST:
        """Create a serial device from the given URL.

        :param url: URL to use for the device.
        :param args: Additional arguments to pass to the serial device constructor.
        :param kwargs: Additional keyword arguments to pass to the serial device constructor.

        :return: Serial device created from the given URL.
        """
        return SerialDevice(serial=ser.serial_for_url(url=url, *args, **kwargs))


# -->> API <<---------------------------


# -->> Export <<------------------------
__all__ = [
    "SerialDevice",
]


# -->> Execute <<-----------------------
# Meant as a package, not a script. No code will be executed.
