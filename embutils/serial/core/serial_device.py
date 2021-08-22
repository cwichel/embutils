#!/usr/bin/python
# -*- coding: ascii -*-
"""
Serial device implementation classes.

:date:      2021
:author:    Christian Wiche
:contact:   cwichel@gmail.com
:license:   The MIT License (MIT)
"""

import serial
import time
from embutils.utils import time_elapsed, EventHook, IntEnumMod, LOG_SDK, ThreadItem, UsbID
from serial.tools import list_ports
from typing import List, Tuple, Union


logger_sdk = LOG_SDK.logger


class SerialDevice:
    """
    Serial device implementation. This class can be used to extend the
    python serial class capabilities.

    Available events:

    #.  **on_usb_id_changed:** This event is emitted when the ID of the serial
        device change during connection. Subscribe using callbacks with syntax::

            def <callback>(old_id: UsbID, new_id: UsbID)

    """
    SETTINGS = {
        'baudrate': 115200,
        'bytesize': 8,
        'stopbits': 1,
        'parity':   'N',
        'timeout':  0.1
        }

    def __init__(self, port: str = None, uid: UsbID = None, settings: dict = None, looped: bool = False) -> None:
        """
        Class initialization.

        :param str port:        Port in which the serial device is connected.
        :param UsbID uid:       Device USB ID.
        :param dict settings:   Device configuration.
        :param bool looped:     Enable the test mode (looped serial).
        """
        # Initialize values
        self._id: Union[None, UsbID] = None

        # Check settings
        if not isinstance(settings, dict):
            settings = self.SETTINGS

        # Events
        self.on_usb_id_changed = EventHook()

        # Check if test mode
        if looped:
            # Yes -> Configure looped
            # Ask for ID
            if not isinstance(uid, UsbID):
                raise ValueError('Test UsbID is required for looped mode!')
            # Configure
            self._serial = serial.serial_for_url(url='loop://', exclusive=True)
            self._serial.apply_settings(d=settings)
            self._id = uid
        else:
            # No -> Configure normal
            # Ask for port
            if not isinstance(port, str):
                msg = 'Serial port is required!'
                logger_sdk.error(msg)
                raise ValueError(msg)
            # Get ID if needed
            if not isinstance(uid, UsbID):
                uid = self._get_id_from_port(port=port)
                if uid is None:
                    msg = 'Serial port is not connected!'
                    logger_sdk.error(msg)
                    raise ValueError(msg)
            # Prepare port
            self._serial = serial.Serial(exclusive=True)
            self._serial.apply_settings(d=settings)
            self._serial.port = port
            self._id = uid

        # Log creation
        logger_sdk.info(f'Device created: port={self._serial.port}, id={self._id}.')

    def __repr__(self) -> str:
        """
        Representation string.

        :returns: Representation string.
        :rtype: str
        """
        return f'{self.__class__.__name__}(port={self._serial.port}, usb_id={self._id})'

    def __eq__(self, other: 'SerialDevice') -> bool:
        """
        Check if two objects are equal.

        :param Frame other: Instance of class to compare.

        :returns: True if equal, false otherwise.
        :rtype: bool
        """
        return (self._serial.port == other.port) and (self._id == other.id)

    @property
    def serial(self) -> serial.Serial:
        """
        Serial handler.
        """
        return self._serial

    @property
    def port(self) -> str:
        """
        Device port name.
        """
        return self._serial.port

    @property
    def id(self) -> UsbID:
        """
        Device USB ID.
        """
        return self._id

    @property
    def timeout(self) -> float:
        """
        Serial process timeout.
        """
        return self._serial.timeout

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        """
        Set the serial process timeout.

        :param float timeout: Timeout in seconds.
        """
        if timeout <= 0.0:
            raise ValueError('The response timeout needs to be greater than zero.')
        self._serial.timeout = timeout

    @property
    def is_open(self) -> bool:
        """
        Returns if the serial device is open.
        """
        return self._serial.is_open

    def open(self) -> bool:
        """
        Tries to open the serial device port.

        :returns: True if open, false otherwise.
        :rtype: bool
        """
        # Check if port is available
        if self._serial.port is None:
            return False

        # Update USB ID
        usb_id = self._get_id_from_port(port=self._serial.port)
        if usb_id is None:
            logger_sdk.error(f'Port {self._serial.port} is not connected')
            return False
        elif usb_id != self._id:
            logger_sdk.error(f'Port {self._serial.port} has changed its ID!')
            ThreadItem(
                name=f'{self.__class__.__name__}.on_list_change',
                target=lambda: self.on_usb_id_changed.emit(old_id=self._id, new_id=usb_id)
                )
            self._id = usb_id

        # Try to connect
        try:
            if self._serial.is_open:
                logger_sdk.info(f'Port {self._serial.port} already open.')
                return True
            else:
                self._serial.open()
                logger_sdk.info(f'Port {self._serial.port} opened.')
                return True

        except serial.SerialException as ex:
            logger_sdk.error(f'Port {self._serial.port} has connection issues. {ex}')
            return False

    def close(self) -> None:
        """
        Closes the serial device port.
        """
        if self._serial.is_open:
            self.flush()
            self._serial.close()
            logger_sdk.info(f'Port {self._serial.port} closed.')

    def flush(self) -> None:
        """
        Flush the serial device buffer.
        """
        try:
            if self._serial.is_open:
                self._serial.flush()
        except serial.SerialException:
            pass

    def write(self, data: bytearray) -> int:
        """
        Write the given byte array through the device serial port.

        :param bytearray data: Bytes to be sent through the serial port.

        :returns: Number of bytes sent.
        :rtype: int
        """
        if self._serial.is_open:
            return self._serial.write(data=data)
        return 0

    def read(self, size: int = 1) -> Union[None, bytearray]:
        """
        Read a fixed number of bytes from the serial buffer. The process is
        stopped with error if a timeout is reached before completion.

        :param int size: Number of bytes to read.

        :returns: None if empty or disconnected. Bytearray in case of bytes received.
        :rtype: Union[None, bytearray]
        """
        try:
            if self._serial.is_open:
                return self._serial.read(size=size)
        except serial.SerialException as ex:
            logger_sdk.error(f'Port {self._serial.port} has connection issues. {ex}')
            return None

    def read_until(self, expected: bytes = b'\n', size: int = None) -> Union[None, bytearray]:
        """
        Read bytes from the serial buffer until the expected sequence is found,
        the received bytes exceed the specified limit or a timeout is reached.

        :param bytes expected:  Stop read condition.
        :param int size:        Read array size limit.

        :returns: None if empty or disconnected. Bytearray in case of bytes received.
        :rtype: Union[None, bytearray]
        """
        try:
            if self._serial.is_open:
                return self._serial.read_until(expected=expected, size=size)
        except serial.SerialException as ex:
            logger_sdk.error(f'Port {self._serial.port} has connection issues. {ex}')
            return None

    @staticmethod
    def _get_id_from_port(port: str) -> Union[None, UsbID]:
        """
        Gets the USB ID form the given port.

        :param str port: Target serial device port.

        :returns: None if device is not connected, USB ID otherwise.
        :rtype: Union[None, UsbID]
        """
        dev_list = SerialDeviceList.scan().filter(port=port)
        if dev_list:
            return dev_list[0].id
        return None


class SerialDeviceList(List[SerialDevice]):
    """
    Serial device list implementation. This class define a list of serial devices
    and implements mechanisms to compare and filter lists.
    """
    def get_changes(self, other: 'SerialDeviceList') -> 'SerialDeviceList':
        """
        Get the differences between two serial device lists.

        :param SerialDeviceList other: List to compare with.

        :returns: List containing the filtered devices.
        :rtype: SerialDeviceList
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

    def filter(self, port: str = None, uid: UsbID = None) -> 'SerialDeviceList':
        """
        Filter serial devices from a given list.

        :param str port:    Required port name.
        :param UsbID uid:   Required USB ID.

        :returns: List containing the filtered devices.
        :rtype: SerialDeviceList
        """
        dev_list = self

        # Filter by port
        if isinstance(port, str):
            dev_list = SerialDeviceList([dev for dev in dev_list if dev.port == port])

        # Filter by ID
        if isinstance(uid, UsbID):
            dev_list = SerialDeviceList([dev for dev in dev_list if dev.id == uid])

        return dev_list

    @staticmethod
    def scan() -> 'SerialDeviceList':
        """
        Scan the system and return a list with the connected serial devices.

        :returns: List with connected devices.
        :rtype: SerialDeviceList
        """
        dev_list = SerialDeviceList()

        # Get devices
        logger_sdk.info('Scanning serial devices')
        dev_scan = list_ports.comports()
        for dev in dev_scan:
            # Not consider items without ID
            if dev.vid is None or dev.pid is None:
                continue

            # Create device
            new = SerialDevice(port=dev.device, uid=UsbID(vid=dev.vid, pid=dev.pid))
            dev_list.append(new)

        return dev_list


class SerialDeviceScanner:
    """
    Serial device scanner implementation. This class define a thread that allow
    to check periodically for changes on the connected serial devices.

    Available events:

    #.  **on_scan_period:** This event is emitted after the scan period is
        completed. Subscribe using callbacks with syntax::

            def <callback>()

    #.  **on_list_change:** This event is emitted when a change is detected
        on the connected device list. Subscribe using callbacks with syntax::

            def <callback>(event: SerialDeviceScanner.Event, devices: SerialDeviceList)

    """
    class Event(IntEnumMod):
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
        def get_event(old: SerialDeviceList, new: SerialDeviceList) -> Tuple['SerialDeviceScanner.Event', SerialDeviceList]:
            """
            Compares two serial device lists and return the differences.

            :param SerialDeviceList old: Last scanned device list.
            :param SerialDeviceList new: New scanned device list.

            :returns: Serial device scanner event and device difference list.
            :rtype: Tuple[SerialDeviceScanner.Event, SerialDeviceList]
            """
            # Get difference and define event
            diff = old.get_changes(other=new)
            event = SerialDeviceScanner.Event.SD_NO_EVENT
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

    def __init__(self, period: float = 0.5) -> None:
        """
        Class initialization.

        :param float period:    Scanner refresh period in seconds.
        """
        # Define device lists
        self._dev_list      = SerialDeviceList()    # Devices connected
        self._dev_change    = SerialDeviceList()    # List of devices that triggered the event

        # Define scan period
        self._scan_period = period

        # Define events
        self.on_scan_period = EventHook()
        self.on_list_change = EventHook()

        # Start scanner
        self._is_active = True
        self._thread = ThreadItem(name=self.__class__.__name__, target=self._process)

    def __del__(self) -> None:
        """
        Class destructor. Stops the scanner thread.
        """
        self.stop()

    @property
    def is_alive(self) -> bool:
        """
        Returns if the scan thread is alive.
        """
        return self._thread.is_alive()

    @property
    def devices(self) -> SerialDeviceList:
        """
        Connected serial devices list.
        """
        return self._dev_list

    def stop(self) -> None:
        """
        Stops the scanner thread.
        """
        self._is_active = False
        while self._thread.is_alive():
            time.sleep(0.01)
        logger_sdk.info('Scanner stopped.')

    def _scan(self) -> None:
        """
        Scanner functionality:

        #. Read the connected devices.
        #. Check for changes on the connected devices.
        #. Raise change event if required, updates current device list.

        """
        # Get the connected devices
        dev_list = SerialDeviceList.scan()

        # If the change callback has items, inform the differences
        if not self.on_list_change.empty and (dev_list != self._dev_change):
            # Get the changes and generate event
            event, dev_diff = self.Event.get_event(old=self._dev_change, new=dev_list)
            ThreadItem(
                name=f'{self.__class__.__name__}.on_list_change',
                target=lambda: self.on_list_change.emit(event=event, dev_diff=dev_diff)
                )

            # Update the compare list
            self._dev_change = dev_list

        # Update the connected devices list
        self._dev_list = dev_list
        ThreadItem(
            name=f'{self.__class__.__name__}.on_scan_period',
            target=self.on_scan_period.emit
            )

    def _process(self) -> None:
        """
        Scanner process:

        #. Initialize the scanned devices list.
        #. Ensures the periodic scanner execution.

        """
        logger_sdk.info('Scanner started.')

        # Initialize connected devices
        self._dev_list = SerialDeviceList.scan()

        # Execute the first scan
        self._scan()

        # Do this periodically
        last_update = time.time()
        while self._is_active:
            # Wait until the scan period is passed...
            if time_elapsed(last_update) > self._scan_period:
                last_update = time.time()
                self._scan()

            # Let some time pass
            time.sleep(0.01)
