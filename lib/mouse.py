import win32api

from . import utility
from .windowApp import WindowApp
from typing import Dict, List, Tuple, Union

class Mouse():
    def __init__(self) -> None:
        self.is_pressed = win32api.GetKeyState(0x01) < 0

    @property
    def pos(self) -> Tuple[int, int]:
        return win32api.GetCursorPos()

    def get_hovered_windows(self, pos : Tuple[int, int], windows : Dict[int, WindowApp]) -> Dict[int, WindowApp]:
        hovered_windows : Dict[int, WindowApp] = {}

        for window in windows.values():
            if window.exists and window.rect.collidepoint(pos):
                hovered_windows[window.hwnd] = window

        return hovered_windows

    def get_topmost_hovered_window(self, pos : Tuple[int, int], windows : Dict[int, WindowApp]) -> Union[WindowApp, None]:
        hovered_windows = self.get_hovered_windows(pos, windows)
        topmost_hwnd = utility.get_topmost_window(hovered_windows.keys())
        if topmost_hwnd is None:
            return None

        topmost_window = hovered_windows.get(topmost_hwnd, None)
        return topmost_window

    def drag_start(self, pos : Tuple[int, int], windows : List[WindowApp]):
        for window in windows:
            if window.is_valid and window.exists:
                window.on_drag_start(pos, is_topmost=False)

    def drag_stop(self, pos : Tuple[int, int], windows : List[WindowApp]):
        taskbar_rect = utility.get_point_monitor_info(pos).taskbar_rect

        for window in windows:
            if window.is_valid and window.exists:
                window.on_drag_stop(pos, taskbar_rect)

    def on_mouse_down(self, pos : Tuple[int, int], windows : Dict[int, WindowApp]) -> None:
        topmost_window = self.get_topmost_hovered_window(pos, windows)
        if topmost_window is None or not topmost_window.is_taskbar_app or not topmost_window.exists:
            self.drag_start(pos, windows.values()); return

        topmost_window.on_drag_start(pos, is_topmost=True)
        filtered_windows = filter(lambda w: w.hwnd != topmost_window.hwnd, windows.values())

        self.drag_start(pos, filtered_windows)

    def on_mouse_up(self, pos : Tuple[int, int], windows : Dict[int, WindowApp]) -> None:
        self.drag_stop(pos, windows.values())

    def process_updates(self, windows : Dict[int, WindowApp]) -> None:
        key_state = win32api.GetKeyState(0x01) < 0

        if key_state != self.is_pressed:
            self.is_pressed = key_state

            if self.is_pressed:
                self.on_mouse_down(self.pos, windows)
            else:
                self.on_mouse_up(self.pos, windows)
