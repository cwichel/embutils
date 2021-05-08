#!/usr/bin/python
# -*- coding: ascii -*-
"""
Keyboard input handling.

@date:      2021
@author:    Christian Wiche
@contact:   cwichel@gmail.com
@license:   The MIT License (MIT)
"""

import pygetwindow as window
import time
from embutils.utils.events import EventHook
from embutils.utils.threading import ThreadItem
from pynput.keyboard import Key, KeyCode, Listener
from typing import Union


class KeyLogger:
    """Simple keyboard logger implementation.

    NOTE: Log all the key inputs on the system

    The available events are:
        1. on_press: This event is emitted when a key is pressed.
            Subscribe using callback with syntax:
                def <callback> (key: Key)

        2. on_release: This event is emitted when a key is released.
            Subscribe using callback with syntax:
                def <callback> (key: Key)
    """
    def __init__(self, app_only: bool = True) -> None:
        """Class initialization.
        Define the class events and start the thread.

        Args:
            app_only (bool): If true, log keyboard events when the app is
                focused. Log all events otherwise.
        """
        # Events
        self.on_press = EventHook()
        self.on_release = EventHook()

        # Filter
        self._app_only = app_only
        self._app_window = window.getActiveWindow()

        # Thread
        self._is_active = True
        self._kb_thread = Listener(on_press=self._on_press, on_release=self._on_release, daemon=True)
        self._main_thread = ThreadItem(name=self.__class__.__name__, target=self._process)

    def _on_app_window(self) -> bool:
        """Return if the main window is selected.

        Returns:
            bool: Main window selected
        """
        active_window = window.getActiveWindow()
        return self._app_window == active_window

    def _on_press(self, key: Union[Key, KeyCode]) -> None:
        """Internal use: Emit the pressed key event.

        Args:
            key (Union[Key, KeyCode]): Pressed key info.
        """
        # Filter events (if needed)
        if self._app_only and not self._on_app_window():
            return
        # Generate event
        self.on_press.emit(key=key)

    def _on_release(self, key: Union[Key, KeyCode]) -> None:
        """Internal use: Emit the key released event.

        Args:
            key (Union[Key, KeyCode]): Pressed key info.
        """
        # Filter events (if needed)
        if self._app_only and not self._on_app_window():
            return
        # Generate event
        self.on_release.emit(key=key)

    def _process(self) -> None:
        """Keyboard logger thread process.
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

    def join(self) -> None:
        """Maintain the program alive until this thread is
        asked to stop.
        """
        while self._is_active:
            time.sleep(1)
