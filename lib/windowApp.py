import random, noise, win32gui, win32con
from .monitorInfo import MonitorInfo
from .utility import path_exists_in_list, constrain
from typing import List, Union

class WindowApp():
    def __init__(self, hwnd : int, exe_path : str, monitor_info : MonitorInfo) -> None:
        self.hwnd = hwnd
        self.exe_path = exe_path
        self.monitor_info = monitor_info
        self.valid = False

        random_sample = random.sample(range(0, 1000), 2)
        self.noise_time_x = random_sample[0]
        self.noise_time_y = random_sample[1]

    @property
    def title(self) -> Union[str, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        return win32gui.GetWindowText(self.hwnd)

    @property
    def width(self) -> Union[int, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        rect = win32gui.GetWindowRect(self.hwnd)
        return rect[2] - rect[0]

    @property
    def height(self) -> Union[int, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        rect = win32gui.GetWindowRect(self.hwnd)
        return rect[3] - rect[1]

    @property
    def is_maximized(self) -> Union[bool, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        tup = win32gui.GetWindowPlacement(self.hwnd)
        return tup[1] == win32con.SW_SHOWMAXIMIZED

    @property
    def is_minimized(self) -> Union[bool, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        tup = win32gui.GetWindowPlacement(self.hwnd)
        return tup[1] == win32con.SW_SHOWMINIMIZED

    @property
    def is_foreground(self) -> Union[bool, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        return win32gui.GetForegroundWindow() == self.hwnd

    @property
    def is_normal(self) -> Union[bool, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        tup = win32gui.GetWindowPlacement(self.hwnd)
        return tup[1] == win32con.SW_SHOWNORMAL

    def validate(self, blacklisted_paths : List[str], whitelisted_paths : List[str]) -> None:
        if self.exe_path is None or self.monitor_info is None:
            self.valid = False; return

        style : int    = win32gui.GetWindowLong(self.hwnd, win32con.GWL_STYLE)
        ex_style : int = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        
        is_in_taskbar = (style | ex_style) & (win32con.WS_OVERLAPPED | win32con.WS_EX_APPWINDOW | win32con.WS_EX_OVERLAPPEDWINDOW)
        is_popup = style & win32con.WS_POPUP

        if not is_in_taskbar or is_popup:
            self.valid = False; return

        if path_exists_in_list(self.exe_path, whitelisted_paths):
            self.valid = True; return

        self.valid = not path_exists_in_list(self.exe_path, blacklisted_paths)

    def move(self, x : int, y : int) -> None:
        try:
            win32gui.MoveWindow(self.hwnd, int(x), int(y), self.width, self.height, 1)

        except win32gui.error as e:
            if e.args[0] == 5:
                print(f"WARNING: No permission to move window: \'{self.title}\' at \'{self.exe_path}\'!")
            else:
                print(f"ERROR: Error raised while trying to move window: \'{self.title}\' at \'{self.exe_path}\'!")

    def move_random(self) -> None:
        if not win32gui.IsWindow(self.hwnd) or not self.is_normal:
            return

        work_area = self.monitor_info.work_area
        pos_x = random.randint(5, max(work_area[2] - self.width  - 5, 5))
        pos_y = random.randint(5, max(work_area[3] - self.height - 5, 5))

        self.move(work_area[0] + pos_x, work_area[1] + pos_y)

    def move_simplex_random(self, speed : float, octaves=1, persistence=0.5, lacunarity=2, base=0) -> None:
        if not win32gui.IsWindow(self.hwnd) or not self.is_normal:
            return

        noise_x = noise.snoise2(self.noise_time_x, self.noise_time_x, 
            octaves=octaves, persistence=persistence, lacunarity=lacunarity, base=base)

        noise_y = noise.snoise2(self.noise_time_y, self.noise_time_y, 
            octaves=octaves, persistence=persistence, lacunarity=lacunarity, base=base)

        self.noise_time_x += speed
        self.noise_time_y += speed

        work_area = self.monitor_info.work_area
        noise_x = constrain(noise_x, -1, 1, 5, max(work_area[2] - self.width  - 5, 5))
        noise_y = constrain(noise_y, -1, 1, 5, max(work_area[3] - self.height - 5, 5))

        self.move(work_area[0] + noise_x, work_area[1] + noise_y)
