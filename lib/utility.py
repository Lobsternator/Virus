import psutil, win32api, win32con, win32gui, win32process

from .monitorInfo import MonitorInfo
from typing import List, Union

def sort_windows(windows : List[int]) -> List[int]:
    sorted_windows : List[int] = []

    top_window = win32gui.FindWindow(None, None)
    if not top_window:
        return sorted_windows

    if top_window in windows:
        sorted_windows.append(top_window)

    current_window = top_window
    while True:
        current_window = win32gui.GetWindow(current_window, win32con.GW_HWNDNEXT)
        if not current_window:
            break

        if current_window in windows:
            sorted_windows.append(current_window)

    return sorted_windows

def get_topmost_window(windows : List[int]) -> int:
    sorted_windows = sort_windows(windows)
    if len(sorted_windows) == 0:
        return None

    return sorted_windows[0]

def get_window_executable_path(hwnd) -> Union[str, None]:
    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    
    try:
        return psutil.Process(pid).exe()

    except psutil.NoSuchProcess:
        print(f"WARNING: Couldn't find executable path for window: \'{win32gui.GetWindowText(hwnd)}\'!")
        return None

def get_monitor_info(hwnd : int) -> Union[MonitorInfo, None]:
    try:
        return MonitorInfo(win32api.GetMonitorInfo(win32api.MonitorFromWindow(hwnd)))
    except win32api.error as e:
        if e.args[0] == 1461:
            print(f"WARNING: Couldn't find monitor info for window: \'{win32gui.GetWindowText(hwnd)}\'!")
            return None
        else:
            raise e

def path_exists_in_list(path : str, path_list : List[str]) -> bool:
    return any([path.find(listed_path) != -1 for listed_path in path_list])

def clamp(value : float, value_min : float, value_max : float) -> float:
    return min(max(value, value_min), value_max)

def constrain(value : float, in_min : float, in_max : float, out_min : float, out_max : float) -> float:
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
