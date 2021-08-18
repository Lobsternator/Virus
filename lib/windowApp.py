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
    def is_maximized(self) -> Union[int, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        tup = win32gui.GetWindowPlacement(self.hwnd)
        result = None

        if tup[1] == win32con.SW_SHOWMAXIMIZED:
            result = 1
        else:
            result = 0

        return result

    @property
    def is_minimized(self) -> Union[int, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        tup = win32gui.GetWindowPlacement(self.hwnd)
        result = None

        if tup[1] == win32con.SW_SHOWMINIMIZED:
            result = 1
        else:
            result = 0

        return result

    @property
    def is_foreground(self) -> Union[int, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        if win32gui.GetForegroundWindow() == self.hwnd:
            return 1
        else:
            return 0

    @property
    def is_normal(self) -> Union[int, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        tup = win32gui.GetWindowPlacement(self.hwnd)
        result = None

        if tup[1] == win32con.SW_SHOWNORMAL:
            result = 1
        else:
            result = 0

        return result

    def validate(self, blacklisted_paths : List[str], whitelisted_paths : List[str]) -> None:
        if self.exe_path is None or self.monitor_info is None or self.title == '':
            self.valid = False; return
        
        if self.exe_path.find("explorer.exe") != -1 and self.title == "Drag":
            self.valid = False; return

        if path_exists_in_list(self.exe_path, whitelisted_paths):
            self.valid = True; return

        self.valid = not path_exists_in_list(self.exe_path, blacklisted_paths)

    def move(self, x : int, y : int) -> None:
        if not win32gui.IsWindow(self.hwnd) or not self.is_normal:
            return

        try:
            win32gui.MoveWindow(self.hwnd, int(x), int(y), self.width, self.height, 1)

        except Exception as e:
            if e.args[0] == 5:
                print(f"WARNING: No permission to move window \'{self.title}\' at \'{self.exe_path}\'!")
            else:
                print(f"ERROR: Error raised while trying to move window \'{self.title}\' at \'{self.exe_path}\'!")

    def move_random(self) -> None:
        if not win32gui.IsWindow(self.hwnd) or not self.is_normal:
            return

        work_area = self.monitor_info.work_area
        monitor_rect = self.monitor_info.monitor_rect

        pos_x = random.randint(work_area[0] + 5, max(work_area[2] - self.width  - 5, 5))
        pos_y = random.randint(work_area[1] + 5, max(work_area[3] - self.height - 5, 5))

        self.move(monitor_rect[0] + pos_x, monitor_rect[1] + pos_y)

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
        monitor_rect = self.monitor_info.monitor_rect

        noise_x = constrain(noise_x, -1, 1, work_area[0] + 5, max(work_area[2] - self.width  - 5, 5))
        noise_y = constrain(noise_y, -1, 1, work_area[1] + 5, max(work_area[3] - self.height - 5, 5))

        self.move(monitor_rect[0] + noise_x, monitor_rect[1] + noise_y)
