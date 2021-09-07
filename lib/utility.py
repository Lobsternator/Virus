import psutil, win32api, win32con, win32gui, win32process

from .monitorInfo import MonitorInfo
from .rect import Rect
from ctypes import Structure, sizeof
from ctypes.wintypes import DWORD, HWND, RECT
from typing import Dict, Iterable, List, Tuple, Union

class GUITHREADINFO(Structure):
    cbSize : DWORD
    flags : DWORD
    hwndActive : HWND
    hwndFocus : HWND
    hwndCapture : HWND
    hwndMenuOwner : HWND
    hwndMoveSize : HWND
    hwndCaret : HWND
    rcCaret : RECT

    _fields_ = [
		('cbSize', DWORD),
		('flags', DWORD),
		('hwndActive', HWND),
		('hwndFocus', HWND),
		('hwndCapture', HWND),
		('hwndMenuOwner', HWND),
		('hwndMoveSize', HWND),
		('hwndCaret', HWND),
		('rcCaret', RECT),
	]

def create_thread_info():
    return GUITHREADINFO(cbSize=sizeof(GUITHREADINFO))

def sort_windows(windows : Iterable[int]) -> List[int]:
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

def get_topmost_window(windows : Iterable[int]) -> int:
    sorted_windows = sort_windows(windows)
    if len(sorted_windows) == 0:
        return None

    return sorted_windows[0]

def get_window_executable_path(hwnd : int) -> Union[str, None]:
    if not win32gui.IsWindow(hwnd):
        return None

    pid = win32process.GetWindowThreadProcessId(hwnd)[1]

    try:
        return psutil.Process(pid).exe()

    except psutil.NoSuchProcess:
        print(f"WARNING: Couldn't find executable path for window: \'{win32gui.GetWindowText(hwnd)}\'!")
        return None

def convert_rect(win32_rect : Tuple[int, int, int, int]) -> Rect:
    x = win32_rect[0]
    y = win32_rect[1]
    width = win32_rect[2] - win32_rect[0]
    height = win32_rect[3] - win32_rect[1]

    return Rect(x, y, width, height)

def convert_monitor_info(win32_monitor_info : Dict[str, Tuple[int, int, int, int]]) -> MonitorInfo:
    monitor_rect = convert_rect(win32_monitor_info.get("Monitor"))
    work_area = convert_rect(win32_monitor_info.get("Work"))

    return MonitorInfo(monitor_rect, work_area)

def get_window_monitor_info(hwnd : int) -> Union[MonitorInfo, None]:
    if not win32gui.IsWindow(hwnd):
        return None

    try:
        return convert_monitor_info(win32api.GetMonitorInfo(win32api.MonitorFromWindow(hwnd)))

    except win32api.error as e:
        if e.args[0] == 1461:
            print(f"WARNING: Couldn't find monitor info from window: \'{win32gui.GetWindowText(hwnd)}\'! Using default instead.")
            return convert_monitor_info(win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0))))
        else:
            raise e

def get_point_monitor_info(point : Tuple[int, int]) -> MonitorInfo:
    try:
        return convert_monitor_info(win32api.GetMonitorInfo(win32api.MonitorFromPoint((int(point[0]), int(point[1])))))
        
    except win32api.error as e:
        if e.args[0] == 1461:
            print(f"WARNING: Couldn't find monitor info from point: ({point[0]}, {point[1]})! Using default instead.")
            return convert_monitor_info(win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0))))
        else:
            raise e

def path_exists_in_list(path : str, path_list : Iterable[str]) -> bool:
    for p in path_list:
        if path.find(p) != -1:
            return True

    return False

def clamp(value : float, value_min : float, value_max : float) -> float:
    return min(max(value, value_min), value_max)

def constrain(value : float, in_min : float, in_max : float, out_min : float, out_max : float) -> float:
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def lerp(pos_1 : Tuple[int, int], pos_2 : Tuple[int, int], factor : float) -> Tuple[int, int]:
    lerp_x = pos_1[0] + (pos_2[0] - pos_1[0]) * factor
    lerp_y = pos_1[1] + (pos_2[1] - pos_1[1]) * factor
    
    return (int(lerp_x), int(lerp_y))
