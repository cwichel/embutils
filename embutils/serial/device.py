#!/usr/bin/python
# -*- coding: ascii -*-
"""
Serial device implementation classes.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import threading as th
import time
import typing as tp

import serial
import serial.tools.list_ports

from ..utils import EventHook, IntEnum, SimpleThreadTask, sync, elapsed
from ..utils import SDK_LOG, SDK_TP


# -->> Definitions <<------------------


# -->> API <<--------------------------
class Device:
    """
    Serial device implementation wrapper.
    This class includes the USB ID information and allows easily use of looped serial ports for testing.
    """
    #: Default device ID
    DEF_ID = 0xDEADBEEF

    #: Default device settings
    DEF_SETTINGS = {
        'baudrate': 115200,
        'bytesize': 8,
        'stopbits': 1,
        'parity':   'N',
        'timeout':  0.1
        }

    def __init__(self, port: str = None, looped: bool = False, settings: dict = None) -> None:
        """
        Device configuration.
        Applies the serial device settings to the selected port.

        :param str port:        Port name.
        :param bool looped:     Enables the test mode (looped serial).
        :param dict settings:   Serial device configuration.
        """
        # Prepare settings
        if not isinstance(settings, dict):
            settings = self.DEF_SETTINGS

        # Multi-thread safety
        self._lock = th.RLock()

        # Create serial
        self._loop = looped
        if looped:
            self._serial = serial.serial_for_url(url="loop://", do_not_open=True, exclusive=True)
            self._id = self.DEF_ID
        else:
            # Check port
            if port is None:
                raise ValueError("Port is required!")
            # Get ID
            _id = self._id_from_port(port=port)
            if _id is None:
                raise ValueError(f"Port {port} is not connected!")
            # Initialize
            self._serial = serial.Serial()
            self._serial.port = port
            self._id = _id

        # Configure serial
        self._serial.apply_settings(d=settings)
        SDK_LOG.info(f"Serial device created: {self.__repr__()}")

    def __repr__(self) -> str:
        """
        Representation string.
        """
        return f"{self.__class__.__name__}(port={self.port}, id=0x{self.id:08X}, looped={self._loop})"

    def __eq__(self, other: object) -> bool:
        """
        Check if the object is equal to the input.
        """
        if isinstance(other, self.__class__):
            return (self.port == other.port) and (self.id == other.id)
        return False

    def __ne__(self, other: object):
        """
        Check if the object is different to the input.
        """
        return not self.__eq__(other)

    @property
    def port(self) -> str:
        """
        Device port name.
        """
        return self._serial.port

    @property
    def id(self) -> int:
        """
        Device USB ID.
        """
        return self._id

    @property
    def serial(self) -> serial.Serial:
        """
        Serial handler.
        """
        return self._serial

    @property
    def is_open(self) -> bool:
        """
        Returns if the serial device is open.
        """
        return self._serial.is_open

    @sync(lock_name="_lock")
    def open(self) -> bool:
        """
        Tries to open the serial port.

        :returns: True if open, false otherwise.
        :rtype: bool
        """
        try:
            # Check if port is already open
            if self.is_open:
                SDK_LOG.info(f"Port {self.port} already open!")
                return True
            # Try to open it otherwise
            self._serial.open()
            SDK_LOG.info(f"Port {self.port} opened!")
            return True
        except serial.SerialException as ex:
            # Report open issue
            SDK_LOG.error(f"Port {self.port} is unable to connect: {ex}")
            return False

    @sync(lock_name="_lock")
    def close(self) -> None:
        """
        Closes the serial port.
        """
        if self.is_open:
            self.flush()
            self._serial.close()
            SDK_LOG.info(f"Port {self.port} closed!")

    @sync(lock_name="_lock")
    def flush(self) -> None:
        """
        Flushes the serial buffer.
        """
        if self.is_open:
            self._serial.flush()

    @sync(lock_name="_lock")
    def write(self, data: bytearray) -> int:
        """
        Writes the given data through the serial port.

        :param bytearray data: Bytes to be sent through the serial port.

        :returns: Number of bytes sent.
        :rtype: int
        """
        if self.is_open:
            return self._serial.write(data=data)
        return 0

    @sync(lock_name="_lock")
    def read(self, size: int = 1) -> tp.Optional[bytearray]:
        """
        Reads a fixed number of bytes from the serial buffer. The process is
        stopped with error if a timeout is reached before completion.

        :param int size: Number of bytes to read.

        :returns: None if empty or disconnected. Bytearray if bytes received.
        :rtype: Optional[bytearray]
        """
        try:
            if self.is_open:
                return self._serial.read(size=size)
            return None
        except serial.SerialException as ex:
            SDK_LOG.error(f"Port {self.port} presented connection issues while reading: {ex}")
            return None

    @sync(lock_name="_lock")
    def read_until(self, expected: bytes = b'\n', size: int = None) -> tp.Optional[bytearray]:
        """
        Reads bytes from the serial buffer until the expected sequence is found,
        the received bytes exceed the specified limit or a timeout is reached.

        :param bytes expected:  Stop read condition.
        :param int size:        Read array size limit.

        :returns: None if empty or disconnected. Bytearray if bytes received.
        :rtype: Optional[bytearray]
        """
        try:
            if self.is_open:
                return self._serial.read_until(expected=expected, size=size)
            return None
        except serial.SerialException as ex:
            SDK_LOG.error(f"Port {self.port} presented connection issues while reading: {ex}")
            return None

    @staticmethod
    def _id_from_port(port: str) -> tp.Optional[int]:
        """
        Retrieves the USB ID for the given port.

        :param str port: Port name.

        :returns: USB ID
        :rtype: int
        """
        target = None
        devices = serial.tools.list_ports.comports()
        for dev in devices:
            target = dev if (dev.device == port) else target
        return ((target.vid << 16) | target.pid) if target else None


class DeviceList(tp.List[Device]):
    """
    Serial device list implementation.
    This class define mechanisms to scan, compare and filter lists of devices.
    """
    def diff(self, other: 'DeviceList') -> 'DeviceList':
        """
        Get the differences between two serial device lists.

        :param DeviceList other: List to compare with.

        :returns: List containing the differences.
        :rtype: DeviceList
        """
        if self == other:
            return DeviceList()

        # Define base and comparison target
        if len(self) > len(other):
            base = self
            comp = other
        else:
            base = other
            comp = self

        # Perform comparison
        diff = DeviceList()
        for dev in base:
            if dev not in comp:
                diff.append(dev)
        return diff

    def filter(self, port: str = None, dev_id: int = None) -> 'DeviceList':
        """
        Filter serial devices from a given list.

        :param str port:    Port name to be filtered.
        :param int dev_id:  Device ID to be filtered.

        :returns: List containing the filtered devices.
        :rtype: DeviceList
        """
        dev_list = self
        # Filter by port
        if isinstance(port, str):
            dev_list = DeviceList([dev for dev in dev_list if dev.port == port])
        # Filter by ID
        if isinstance(dev_id, int):
            dev_list = DeviceList([dev for dev in dev_list if dev.id == dev_id])
        return dev_list

    @staticmethod
    def scan() -> 'DeviceList':
        """
        Scan the system and return a list with the connected serial devices.

        :returns: List with devices.
        :rtype: DeviceList
        """
        dev_list = DeviceList()

        # Get devices
        dev_scan = serial.tools.list_ports.comports()
        for dev in dev_scan:
            # Not consider items without ID
            if dev.vid is None or dev.pid is None:
                continue
            # Create device
            try:
                new = Device(port=dev.device)
                dev_list.append(new)
            except ValueError as ex:
                SDK_LOG.debug(f"Unable to create a serial device: {ex}")
                continue
        return dev_list


class DeviceScanner:
    """
    Serial device scanner implementation.
    This class define a thread that allows to check periodically for changes on the
    connected serial devices.

    Available events:

    #.  **on_scan_period:** This event is emitted after the scan period is
        completed. Subscribe using callbacks with syntax::

            def <callback>()

    #.  **on_list_change:** This event is emitted when a change is detected
        on the connected device list. Subscribe using callbacks with syntax::

            def <callback>(event: SerialDeviceScanner.Event, devices: SerialDeviceList)

    """
    class Event(IntEnum):
        """
        Serial device scanner event definitions.
        """
        SD_NO_EVENT         = 0x00      # No event
        SD_LIST_CHANGED     = 0x01      # Serial devices list has changed
        SD_PLUGGED_SINGLE   = 0x02      # A single device was plugged
        SD_PLUGGED_MULTI    = 0x03      # Multiple devices were plugged
        SD_REMOVED_SINGLE   = 0x04      # A single device was unplugged
        SD_REMOVED_MULTI    = 0x05      # Multiple devices were unplugged

        @staticmethod
        def get_event(old: DeviceList, new: DeviceList) -> tp.Tuple['DeviceScanner.Event', DeviceList]:
            """
            Compares two serial device lists and return the differences.

            :param DeviceList old: Last scanned device list.
            :param DeviceList new: New scanned device list.

            :returns: Serial device scanner event and device difference list.
            :rtype: Tuple[DeviceScanner.Event, DeviceList]
            """
            # Get difference list and define event
            diff  = old.diff(other=new)
            etype = DeviceScanner.Event
            if not diff:
                event = etype.SD_NO_EVENT
            elif len(new) > len(old):
                event = etype.SD_PLUGGED_MULTI if (len(diff) > 1) else etype.SD_PLUGGED_SINGLE
            elif len(old) > len(new):
                event = etype.SD_REMOVED_MULTI if (len(diff) > 1) else etype.SD_REMOVED_SINGLE
            else:
                event = etype.SD_LIST_CHANGED
            return event, diff

    def __init__(self, period: float = 0.5) -> None:
        """
        Class initialization.

        :param float period:    Scanner refresh period in seconds.
        """
        # Define device lists
        self._dev_list      = DeviceList()    # Devices connected
        self._dev_change    = DeviceList()    # List of devices that triggered the event

        # Define scan period
        self._scan_period = period

        # Define events
        self.on_scan_period = EventHook()
        self.on_list_change = EventHook()

        # Start scanner
        self._active = True
        self._finished  = False
        SDK_TP.enqueue(task=SimpleThreadTask(
            name=f"{self.__class__.__name__}.process",
            task=self._process
            ))

    def __del__(self) -> None:
        """
        Class destructor. Stops the scanner thread.
        """
        if self.is_alive:
            self.stop()

    @property
    def is_alive(self) -> bool:
        """
        Returns if the scan thread is alive.
        """
        return self._active or not self._finished

    @property
    def devices(self) -> DeviceList:
        """
        Connected serial devices list.
        """
        return self._dev_list

    def stop(self) -> None:
        """
        Stops the scanner thread.
        """
        self._active = False
        while self.is_alive:
            time.sleep(0.01)
        SDK_LOG.info('Scanner stopped.')

    def _scan(self) -> None:
        """
        Scanner functionality:

        #. Read the connected devices.
        #. Check for changes on the connected devices.
        #. Raise change event if required, updates current device list.

        """
        # Get the connected devices
        dev_list = DeviceList.scan()

        # If the change callback has items, inform the differences
        if not self.on_list_change.empty:
            event, dev_diff = self.Event.get_event(old=self._dev_change, new=dev_list)
            if event != self.Event.SD_NO_EVENT:
                SDK_TP.enqueue(task=SimpleThreadTask(
                    name=f'{self.__class__.__name__}.on_list_change',
                    task=lambda: self.on_list_change.emit(event=event, dev_diff=dev_diff)
                    ))
                self._dev_change = dev_list

        # Update the connected devices list
        self._dev_list = dev_list
        SDK_TP.enqueue(task=SimpleThreadTask(
            name=f'{self.__class__.__name__}.on_scan_period',
            task=self.on_scan_period.emit
            ))

    def _process(self) -> None:
        """
        Scanner process:

        #. Initialize the scanned devices list.
        #. Ensures the periodic scanner execution.

        """
        SDK_LOG.info('Scanner started.')

        # Initialize connected devices
        self._dev_list = DeviceList.scan()

        # Execute the first scan
        self._scan()

        # Do this periodically
        last_update = time.time()
        while self._active:
            # Wait until the scan period is passed...
            if elapsed(last_update) > self._scan_period:
                last_update = time.time()
                self._scan()

            # Let some time pass
            time.sleep(0.01)

        # Inform finished
        self._finished = True
