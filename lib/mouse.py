import win32api

from . import utility
from .windowApp import WindowApp
from typing import Dict, Tuple

class Mouse():
    def __init__(self) -> None:
        self.is_pressed = win32api.GetKeyState(0x01) < 0

    @property
    def pos(self) -> Tuple[int, int]:
        return win32api.GetCursorPos()

    def get_hovered_windows(self, pos : Tuple[int, int], windows : Dict[int, WindowApp]) -> Dict[int, WindowApp]:
        hovered_windows : Dict[int, WindowApp] = {}

        for window in windows.values():
            if window.rect.collidepoint(pos):
                hovered_windows[window.hwnd] = window

        return hovered_windows

    def on_mouse_down(self, pos : Tuple[int, int], windows : Dict[int, WindowApp]) -> None:
        try:
            hovered_windows = self.get_hovered_windows(pos, windows)
            topmost_hwnd = utility.get_topmost_window(hovered_windows.keys())
            if topmost_hwnd is None:
                return

            topmost_window = windows.get(topmost_hwnd, None)
            if topmost_window is None or not topmost_window.is_valid:
                return
            
            topmost_window.on_mouse_down(pos, True)
            hovered_windows.pop(topmost_window.hwnd)

        finally:
            for window in hovered_windows.values():
                if window.is_valid:
                    window.on_mouse_down(pos, False)

    def on_mouse_up(self, pos : Tuple[int, int], windows : Dict[int, WindowApp]) -> None:
        for window in windows.values():
            if window.is_valid:
                window.on_mouse_up(pos)

    def process_updates(self, windows : Dict[int, WindowApp]) -> None:
        key_state = win32api.GetKeyState(0x01) < 0

        if key_state != self.is_pressed:
            self.is_pressed = key_state

            if self.is_pressed:
                self.on_mouse_down(self.pos, windows)
            else:
                self.on_mouse_up(self.pos, windows)
