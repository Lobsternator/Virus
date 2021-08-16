import pyautogui, win32process, wmi
from .windowApp import WindowApp
from typing import Dict, List

_c = wmi.WMI()

def process_window_updates(windows : Dict[int, WindowApp]):
    win32_windows : List = pyautogui.getAllWindows()

    for win32_window in win32_windows:
        new_window : WindowApp = windows.get(win32_window._hWnd, None)

        if new_window is None:
            new_window = WindowApp(win32_window)

            windows[win32_window._hWnd] = new_window

    windows_to_pop = []
    for hwnd in windows.keys():
        found_window = len([w for w in win32_windows if w._hWnd == hwnd]) > 0

        if not found_window:
            windows_to_pop.append(hwnd)

    for hwnd in windows_to_pop:
        windows.pop(hwnd)

def get_window_executable_path(window):
    exe = None

    pid = win32process.GetWindowThreadProcessId(window._hWnd)[1]
    query = _c.query('SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s' % str(pid))

    if len(query) > 0:
        exe = query[0].ExecutablePath

    return exe
