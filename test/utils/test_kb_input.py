#!/usr/bin/env python
##
# @file       test_kb_input.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Test keyboard logging utility implementation.
# =============================================================================

from embutils.utils.common import KeyboardLogger, Key, KeyCode
from typing import Union


# Test Definitions ==============================
def key_input_test() -> None:
    """This function implements the basic setup to use this utility.
    NOTES:
        - This test is for manual operation only.
        - All the pressed keys will be shown on console.
        - Modifying the 'app_only' flag will enable logging keys from outside the app window.
        - Pressing ESC will stop the process.
    """
    kb = KeyboardLogger(app_only=True)

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
    key_input_test()
