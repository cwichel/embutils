import time
from embutils.serial_process import SerialDeviceList, SerialDeviceEvent, SerialDeviceScanner


# Example Definitions ===========================
def on_change_handler(event: SerialDeviceEvent, dev_diff: SerialDeviceList) -> None:
    """Process the serial device change event.

    Args:
        event (SerialDeviceEvent): Serial scanner event.
        dev_diff (SerialDeviceList): Change list.
    """
    dev = '\r\n\t'.join('{}'.format(item) for item in dev_diff)
    msg = '{}\r\n\t{}'.format(event.__repr__(), dev)
    print(msg)


def example_serial() -> None:
    """Example execution.
    """
    # Create a serial scanner instance
    ss = SerialDeviceScanner(scan_period=0.05)
    ss.on_list_change += on_change_handler

    # Maintain this alive
    while True:
        time.sleep(0.01)


# Example Execution =============================
if __name__ == '__main__':
    example_serial()
