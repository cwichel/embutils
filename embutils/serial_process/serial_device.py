#!/usr/bin/env python
##
# @file       serial_device.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Serial device implementation.
# =============================================================================

import serial
from typing import List
from serial.tools import list_ports
from embutils.utils.common import UsbID, LOG_SDK

logger_sdk = LOG_SDK.logger


class SerialDevice:
    """Serial device implementation.
    This class can be used to extend the Serial class capabilities.
    """
    SETTINGS = {
        'baudrate': 115200,
        'bytesize': 8,
        'stopbits': 1,
        'parity':   'N',
        'timeout':  0.1
        }

    def __init__(self, port: str = None, usb_id: UsbID = None, settings: dict = None, looped: bool = False) -> None:
        """Class constructor. Initializes the serial device.

        Args:
            port (str): Port in which the serial device is connected.
            usb_id (UsbID): Serial device USB ID.
            settings (dict): Serial device configuration.
            looped (bool): Enable the test mode (looped serial).
        """
        # Check settings
        if not isinstance(settings, dict):
            settings = self.SETTINGS

        # Check if test mode
        if looped:
            # Yes -> Configure looped
            # Ask for ID
            if not isinstance(usb_id, UsbID):
                raise ValueError('Test UsbID is required for looped mode!')
            # Configure
            self._serial = serial.serial_for_url(url='loop://', exclusive=True)
            self._serial.apply_settings(d=settings)
            self._id = usb_id
        else:
            # No -> Configure normal
            # Prepare port
            self._serial = serial.Serial(exclusive=True)
            self._serial.apply_settings(d=settings)
            # Configure depending on inputs
            has_port = isinstance(port, str)
            has_id   = isinstance(usb_id, UsbID)
            if has_port and has_id:
                self._serial.port = port
                self._id = usb_id
            elif has_port:
                dev_list = SerialDeviceList.scan().filter(port=port)
                if dev_list:
                    self._serial.port = port
                    self._id = dev_list[0].id
            elif has_id:
                dev_list = SerialDeviceList.scan().filter(usb_id=usb_id)
                if dev_list:
                    self._serial.port = dev_list[0].port
                    self._id = usb_id

    def __repr__(self) -> str:
        """Get the class representation string.

        Return:
            str: Class representation string.
        """
        return '<{}: port={}, usb_id={}>'.format(self.__class__.__name__, self.port, self.id)

    def __eq__(self, other: 'SerialDevice') -> bool:
        """Compare two serial devices.

        Returns:
            bool: True if equal, false otherwise.
        """
        return (self.port == other.port) and (self.id == other.id)

    @property
    def serial(self) -> serial.Serial:
        """Serial port handler object.

        Returns:
            serial.Serial: Serial interface.
        """
        return self._serial

    @property
    def port(self) -> str:
        """Serial device port.

        Returns:
            str: Serial device port name.
        """
        return self._serial.port

    @port.setter
    def port(self, port: str) -> None:
        """Set the serial device port.

        Args:
            port (str): Serial port name.
        """
        self._serial.port = port

    @property
    def id(self) -> UsbID:
        """Serial device USB ID.

        Returns:
            UsbID: USB ID.
        """
        return self._id

    @id.setter
    def id(self, usb_id: UsbID) -> None:
        """Set the serial device USB ID.

        Args:
            usb_id (UsbID): USB ID value.
        """
        self._id = usb_id

    @property
    def timeout(self) -> float:
        """Serial device operation timeout.

        Return:
            float: Serial device operation timeout.
        """
        return self._serial.timeout

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        """Set the serial device operation timeout.

        Args:
            timeout (float): Serial operation timeout.
        """
        self._serial.timeout = timeout

    @property
    def is_open(self) -> bool:
        """Check if the serial device is open.

        Returns:
            bool: True if open, false otherwise.
        """
        return self._serial.is_open

    def open(self) -> bool:
        """Tries to open the serial device connection.

        Returns:
            bool: True if succeed, false otherwise.
        """
        # Check if port is available
        if self._serial.port is None:
            logger_sdk.debug(msg='Port is not defined.')
            return False

        # Try to connect
        try:
            if self._serial.is_open:
                logger_sdk.debug(msg='Port {} already open.'.format(self.port))
                return True
            else:
                logger_sdk.debug(msg='Opening serial device on port {}...'.format(self.port))
                self._serial.open()
                logger_sdk.debug(msg='Port {} opened successfully.'.format(self.port))
                return True
        except serial.SerialException as ex:
            logger_sdk.debug("Port {} couldn't be opened. {}".format(self.port, ex))
            return False





class SerialDeviceList(List[SerialDevice]):
    """Serial device list implementation.
    Can be used to list the connected serial devices.
    """
    def get_changes(self, other: 'SerialDeviceList') -> 'SerialDeviceList':
        """Get the differences between two serial device lists.

        Args:
            other (SerialDeviceList): List to compare with.

        Return:
            SerialDeviceList: List containing the filtered devices.
        """
        if self == other:
            return SerialDeviceList()

        # Define base and comparison target
        if len(self) > len(other):
            base = self
            comp = other
        else:
            base = other
            comp = self

        # Perform comparison
        diff = SerialDeviceList()
        for dev in base:
            if dev not in comp:
                diff.append(dev)
        return diff

    def filter(self, port: str = None, usb_id: UsbID = None) -> 'SerialDeviceList':
        """Filter elements on the serial device list.

        Args:
            port (str): Port of interest.
            usb_id (UsbID): Device ID of interest.

        Return:
            SerialDeviceList: List containing filtered devices.
        """
        dev_list = self

        # Filter by port
        if isinstance(port, str):
            dev_list = SerialDeviceList([dev for dev in dev_list if dev.port == port])

        # Filter by ID
        if isinstance(usb_id, UsbID):
            dev_list = SerialDeviceList([dev for dev in dev_list if dev.id == usb_id])

        return dev_list

    @staticmethod
    def scan() -> 'SerialDeviceList':
        """Scan the system for available serial ports.

        Return:
            SerialDeviceList: List including all the connected ports.
        """
        dev_list = SerialDeviceList()

        # Get devices
        dev_scan = list_ports.comports()
        for dev in dev_scan:
            # Not consider items without ID
            if dev.vid is None or dev.pid is None:
                continue

            # Create device
            new = SerialDevice(port=dev.device, usb_id=UsbID(vid=dev.vid, pid=dev.pid))
            dev_list.append(new)

        return dev_list
