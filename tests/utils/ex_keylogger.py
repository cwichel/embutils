#!/usr/bin/python
# -*- coding: ascii -*-
"""
Key logger usage test.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

from embutils.utils import KeyLogger, Key, KeyCode
from typing import Union


# Test Definitions ==============================
def test_key_input() -> None:
    """This function implements the basic setup to use this utility.
    NOTES:
        - This test is for manual operation only.
        - All the pressed keys will be shown on console.
        - Modifying the 'app_only' flag will enable logging keys from outside the app window.
        - Pressing ESC will stop the process.
    """
    kb = KeyLogger(app_only=True)

    def on_release(key: Union[Key, KeyCode]):
        nonlocal kb
        print(key)
        if key == Key.esc:
            print("ESC key pressed. Stopping thread...")
            kb.stop()

    kb.on_release += on_release
    kb.join()


# Test Execution ================================
if __name__ == '__main__':
    test_key_input()
