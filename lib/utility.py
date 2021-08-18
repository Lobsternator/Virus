import win32process, win32api, win32gui, psutil
from .monitorInfo import MonitorInfo
from typing import List, Union

def get_window_executable_path(window) -> Union[str, None]:
    pid = win32process.GetWindowThreadProcessId(window._hWnd)[1]
    
    try:
        return psutil.Process(pid).exe()

    except psutil.NoSuchProcess:
        print(f"WARNING: Couldn't find executable path for window: \'{window.tile}\'!")
        return None

def get_monitor_info(hwnd : int, exe_path : str) -> Union[MonitorInfo, None]:
    try:
        return MonitorInfo(win32api.GetMonitorInfo(win32api.MonitorFromWindow(hwnd)))
    except Exception as e:
        if e.args[0] == 1461:
            print(f"WARNING: Couldn't find monitor info for window: \'{win32gui.GetWindowText(hwnd)}\'!")
        else:
            print(f"ERROR: Error raised while getting monitor info for window \'{win32gui.GetWindowText(hwnd)}\' at \'{exe_path}\'! Error: {e}")

        return None

def path_exists_in_list(path : str, path_list : List[str]) -> bool:
    return any([path.find(listed_path) != -1 for listed_path in path_list])

def clamp(value : float, value_min : float, value_max : float) -> float:
    return min(max(value, value_min), value_max)

def constrain(value : float, in_min : float, in_max : float, out_min : float, out_max : float) -> float:
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
