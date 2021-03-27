#!/usr/bin/env python
##
# @file       kb_input.py
# @author     cwichel
# @date       2021
# @copyright  The MIT License (MIT)
# @brief      Keyboard input handlers.
# =============================================================================

import time
from pynput.keyboard import Key, Listener
from embutils.utils.common.events import EventHook
from embutils.utils.common.threading import ThreadItem


class KeyboardInput:
    """Simple keyboard logger implementation.

    The available events are:
        1. on_press: This event is emitted when a key is pressed.
            Subscribe using callback with syntax:
                def <callback> (key: Key)

        2. on_release: This event is emitted when a key is released.
            Subscribe using callback with syntax:
                def <callback> (key: Key)
    """
    def __init__(self):
        """Class initialization.
        Define the class events and start the thread.
        """
        # Events
        self.on_press = EventHook()
        self.on_release = EventHook()

        # Thread
        self._is_active = True
        self._kb_thread = Listener(on_press=self._on_press, on_release=self._on_release, daemon=True)
        self._main_thread = ThreadItem(name=self.__class__.__name__, target=self._process)

    def _on_press(self, key: Key) -> None:
        """Internal use: Emit the pressed key event.
        """
        self.on_press.emit(key=key)

    def _on_release(self, key: Key) -> None:
        """Internal use: Emit the key released event.
        """
        self.on_release.emit(key=key)

    def _process(self) -> None:
        """Keyboard lgo thread process.
        """
        self._kb_thread.start()
        while self._is_active:
            time.sleep(0.01)

    def stop(self) -> None:
        """Stop the thread process.
        """
        self._is_active = False
        while self._main_thread.is_alive():
            time.sleep(0.1)

    def join(self):
        """Utility to maintain the program alive until this
        thread is stopped.
        """
        while self._is_active:
            time.sleep(1)
