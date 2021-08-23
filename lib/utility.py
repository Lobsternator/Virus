import contextlib, psutil, win32api, win32con, win32gui, win32process

with contextlib.redirect_stdout(None):
    from pygame import rect as pyrect

from .monitorInfo import MonitorInfo
from typing import List, Tuple, Union

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

def convert_rect(win32_rect) -> pyrect.Rect:
    x = win32_rect[0]
    y = win32_rect[1]
    width = win32_rect[2] - win32_rect[0]
    height = win32_rect[3] - win32_rect[1]

    return pyrect.Rect(x, y, width, height)

def path_exists_in_list(path : str, path_list : List[str]) -> bool:
    return any([path.find(listed_path) != -1 for listed_path in path_list])

def clamp(value : float, value_min : float, value_max : float) -> float:
    return min(max(value, value_min), value_max)

def constrain(value : float, in_min : float, in_max : float, out_min : float, out_max : float) -> float:
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def lerp(pos_1 : Tuple[int, int], pos_2 : Tuple[int, int], factor : float) -> Tuple[int, int]:
    lerp_x = pos_1[0] * (1 - factor) + pos_2[0] * factor
    lerp_y = pos_1[1] * (1 - factor) + pos_2[1] * factor

    return (int(lerp_x), int(lerp_y))
