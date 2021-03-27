#!/usr/bin/env python
##
# @file       test_kb_input.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Test keyboard logging utility implementation.
# =============================================================================

from embutils.utils.common import KeyboardInput, Key


# Test Definitions ==============================
def key_input_test() -> None:
    """This function implements the basic setup to use this utility.
    NOTES:
        - This test is for manual operation only.
        - All the pressed keys will be shown on console.
        - Pressing ESC will stop the process.
    """
    kb = KeyboardInput()

    def on_release(key: Key):
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
