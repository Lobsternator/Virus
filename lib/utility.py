import pyautogui, win32process, wmi
from .windowApp import WindowApp
from os.path import realpath
from typing import Dict, List, Union

_c = wmi.WMI()

def get_window_executable_path(window) -> Union[str, None]:
    exe_path = None

    pid = win32process.GetWindowThreadProcessId(window._hWnd)[1]
    query = _c.query('SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s' % str(pid))

    if len(query) > 0:
        exe_path = query[0].ExecutablePath

        if exe_path is not None:
            exe_path = realpath(exe_path)

    return exe_path

def process_window_updates(windows : Dict[int, WindowApp], blacklisted_paths : List[str], whitelisted_paths : List[str]) -> None:
    win32_windows : List = pyautogui.getAllWindows()

    for win32_window in win32_windows:
        new_window : WindowApp = windows.get(win32_window._hWnd, None)

        if new_window is None:
            title = win32_window.title
            hwnd = win32_window._hWnd
            exe_path = get_window_executable_path(win32_window)
            
            new_window = WindowApp(title, hwnd, exe_path)
            new_window.validate(blacklisted_paths, whitelisted_paths)

            windows[win32_window._hWnd] = new_window

    windows_to_pop = []
    for hwnd in windows.keys():
        found_window = len([w for w in win32_windows if w._hWnd == hwnd]) > 0

        if not found_window:
            windows_to_pop.append(hwnd)

    for hwnd in windows_to_pop:
        windows.pop(hwnd)
