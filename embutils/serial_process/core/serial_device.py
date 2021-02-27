#!/usr/bin/env python
##
# @file       serial_device.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Serial device implementation.
# =============================================================================

import serial
import time
from enum import IntEnum
from serial.tools import list_ports
from typing import List, Tuple, Union
from embutils.utils.common import UsbID, EventHook, LOG_SDK, ThreadItem


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

        # Log creation
        logger_sdk.info("Device created: port={}, id={}.".format(self.port, self.id))

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
            logger_sdk.error("Can't open port because is not defined.")
            return False

        # Try to connect
        try:
            if self._serial.is_open:
                logger_sdk.info("Port {} already open.".format(self.port))
                return True
            else:
                self._serial.open()
                logger_sdk.info("Port {} opened.".format(self.port))
                return True

        except serial.SerialException as ex:
            logger_sdk.error("Port {} couldn't be opened. {}".format(self.port, ex))
            return False

    def close(self) -> None:
        """Close the serial port.
        """
        if self._serial.is_open:
            self.flush()
            self._serial.close()
            logger_sdk.info("Port {} closed.".format(self.port))

    def flush(self) -> None:
        """Flush the serial port buffer.
        """
        try:
            if self._serial.is_open:
                self._serial.flush()
        except serial.SerialException:
            pass

    def write(self, data: bytearray) -> int:
        """Writes a bytearray through the serial port.

        Args:
            data (bytearray): Bytes to be sent.

        Return:
             int: Bytes sent.
        """
        if self._serial.is_open:
            return self._serial.write(data=data)
        return 0

    def read(self, size: int = 1) -> Union[None, bytearray]:
        """Read a given number of bytes form the serial buffer. The process
        is stopped after the timeout is reached.

        Args:
            size (int): Number oo bytes to read.

        Returns:
            Union[None, bytearray]: None if empty or disconnected. Bytearray in case of bytes received.
        """
        try:
            if self._serial.is_open:
                return self._serial.read(size=size)
        except serial.SerialException as ex:
            logger_sdk.error("Port {} has connection issues. {}".format(self.port, ex))
            return None


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


class SerialDeviceEvent(IntEnum):
    """Serial device scanner events.
    """
    SD_NO_EVENT             = 0x00      # No event
    SD_LIST_CHANGED         = 0x01      # Serial devices list has changed
    SD_PLUGGED_SINGLE       = 0x02      # A single device was plugged
    SD_PLUGGED_MULTI        = 0x03      # Multiple devices were plugged
    SD_REMOVED_SINGLE       = 0x04      # A single device was unplugged
    SD_REMOVED_MULTI        = 0x05      # Multiple devices were unplugged

    @staticmethod
    def get_event(old: SerialDeviceList, new: SerialDeviceList) -> Tuple['SerialDeviceEvent', SerialDeviceList]:
        """Compare the two lists and return the associates scanner event and difference list.

        Args:
            old (SerialDeviceList): Current device list.
            new (SerialDeviceList): Last scanned list.

        Returns:
            SerialDeviceEvent, SerialDeviceList: Scanner event and difference list.
        """
        # Get difference and define event
        diff = old.get_changes(other=new)
        event = SerialDeviceEvent.SD_NO_EVENT
        if len(new) > len(old):
            # Added devices
            event = event.SD_PLUGGED_MULTI if (len(diff) > 1) else event.SD_PLUGGED_SINGLE
        elif len(old) > len(new):
            # Removed devices
            event = event.SD_REMOVED_MULTI if (len(diff) > 1) else event.SD_REMOVED_SINGLE
        else:
            # Same length but different
            event = event.SD_LIST_CHANGED
        return event, diff


class SerialDeviceScanner:
    """Serial device scanner implementation.
    This class can be used to periodically check the serial devices on the system.

    The available events are:
        1. on_scan_period: This event is emitted after every periodic scan.
            Subscribe using callback with syntax:
                def <callback>()

        2. on_list_change: This event is emitted when a change is detected on the device list.
            Subscribe using callback with syntax:
                def <callback>(event: SerialDeviceEvent, devices: SerialDeviceList)
    """
    def __init__(self, scan_period: float = 0.5) -> None:
        """Class constructor. Initializes the serial scanner.

        Args:
            scan_period (float): Scanner refresh period in seconds.
        """
        # Define device lists
        self._dev_list = SerialDeviceList.scan()    # Devices connected
        self._dev_change = SerialDeviceList()       # List of devices that triggered the event

        # Define scan period
        self._scan_period = scan_period

        # Define events
        self.on_scan_period = EventHook()
        self.on_list_change = EventHook()

        # Start scanner
        self._is_active = True
        self._thread = ThreadItem(name=self.__class__.__name__, target=self._process)

    def __del__(self) -> None:
        """Class destructor. Stop the thread.
        """
        self.stop()

    @property
    def is_alive(self) -> bool:
        """Return if the thread is alive.

        Returns:
            bool: True if alive, false otherwise.
        """
        return self._thread.is_alive()

    @property
    def connected_devices(self) -> SerialDeviceList:
        """Return the current scanned device list.

        Returns:
            SerialDeviceList: List with the scanned devices.
        """
        return self._dev_list

    def stop(self) -> None:
        """Stops the serial scanner thread.
        """
        self._is_active = False
        while self._thread.is_alive():
            time.sleep(0.01)
        logger_sdk.info("Scanner stopped.")

    def _scan(self) -> None:
        """This method executed on every period.
        """
        # Get the connected devices
        dev_list = SerialDeviceList.scan()

        # If the change callback has items, inform the differences
        if not self.on_list_change.empty and (dev_list != self._dev_change):
            # Get the changes and generate event
            event, dev_diff = SerialDeviceEvent.get_event(old=self._dev_change, new=dev_list)
            ThreadItem(
                name='{}.{}'.format(self.__class__.__name__, 'on_list_change'),
                target=lambda: self.on_list_change.emit(event=event, dev_diff=dev_diff)
                )

            # Update the compare list
            self._dev_change = dev_list

        # Update the connected devices list
        self._dev_list = dev_list
        ThreadItem(
            name='{}.{}'.format(self.__class__.__name__, 'on_scan_period'),
            target=self.on_scan_period.emit
            )

    def _process(self) -> None:
        """Serial device scanner main process.
        The process consists in:
            1. Read the connected devices.
            2. Compare the new/old lists and generate the change events.
            3. Update connected device lists.
        """
        logger_sdk.info("Scanner started.")

        # Execute the first scan
        self._scan()

        # Do this periodically
        last_update = time.time()
        while self._is_active:
            # Wait until the scan period is passed...
            if (time.time() - last_update) > self._scan_period:
                last_update = time.time()
                self._scan()

            # Let some time pass
            time.sleep(0.01)
