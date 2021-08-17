import pyautogui, win32process, win32api, win32gui, psutil
from .monitorInfo import MonitorInfo
from .windowApp import WindowApp
from typing import Dict, List, Union

def get_window_executable_path(window) -> Union[str, None]:
    pid = win32process.GetWindowThreadProcessId(window._hWnd)[1]
    
    try:
        return psutil.Process(pid).exe()

    except Exception as e:
        print(f"WARNING: Error while getting executable path for window {window.title}! Error: {e}")
        return None

def get_monitor_info(hwnd : int, exe_path : str) -> Union[MonitorInfo, None]:
    try:
        return MonitorInfo(win32api.GetMonitorInfo(win32api.MonitorFromWindow(hwnd)))
    except Exception as e:
        print(f"WARNING: Error while getting monitor info for window \'{win32gui.GetWindowText(hwnd)}\' at \'{exe_path}\'! Error: {e}")
        return None

def process_window_updates(windows : Dict[int, WindowApp], blacklisted_paths : List[str], whitelisted_paths : List[str]) -> None:
    win32_windows : List = pyautogui.getAllWindows()

    for win32_window in win32_windows:
        new_window : WindowApp = windows.get(win32_window._hWnd, None)

        if new_window is None:
            hwnd = win32_window._hWnd
            exe_path = get_window_executable_path(win32_window)
            monitor_info = get_monitor_info(hwnd, exe_path)
            
            new_window = WindowApp(hwnd, exe_path, monitor_info)
            new_window.validate(blacklisted_paths, whitelisted_paths)

            windows[hwnd] = new_window

    windows_to_pop = []
    for hwnd in windows.keys():
        found_window = len([w for w in win32_windows if w._hWnd == hwnd]) > 0

        if not found_window:
            windows_to_pop.append(hwnd)

    for hwnd in windows_to_pop:
        windows.pop(hwnd)
