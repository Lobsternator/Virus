import contextlib, random, noise, win32con, win32gui, win32process

with contextlib.redirect_stdout(None):
    from pygame import rect as pyrect

from ctypes import byref, windll
from . import utility
from typing import List, Tuple, Union

user32 = windll.user32

class WindowApp():
    def __init__(self, hwnd : int) -> None:
        self.hwnd = hwnd
        self.thread_id = win32process.GetWindowThreadProcessId(self.hwnd)[0]
        self.exe_path = utility.get_window_executable_path(self.hwnd)
        self.monitor_info = utility.get_monitor_info(self.hwnd)
        self.is_valid = False
        self.override_drag = False

        self.__thread_info = utility.create_thread_info()

        random_sample = random.sample(range(0, 1000), 2)
        self.noise_time_x = random_sample[0]
        self.noise_time_y = random_sample[1]

    @property
    def exists(self):
        return bool(win32gui.IsWindow(self.hwnd))

    @property
    def title(self) -> Union[str, None]:
        if not self.exists:
            return None

        return win32gui.GetWindowText(self.hwnd)

    @property
    def rect(self) -> Union[pyrect.Rect, None]:
        if not self.exists:
            return None

        rect = win32gui.GetWindowRect(self.hwnd)
        return utility.convert_rect(rect)

    @property
    def drag_rect(self) -> Union[pyrect.Rect, None]:
        _rect = self.rect

        if _rect is not None:
            _rect.height = 50

        return _rect

    @property
    def is_maximized(self) -> Union[bool, None]:
        if not self.exists:
            return None

        tup = win32gui.GetWindowPlacement(self.hwnd)
        return tup[1] == win32con.SW_SHOWMAXIMIZED

    @property
    def is_minimized(self) -> Union[bool, None]:
        if not self.exists:
            return None

        tup = win32gui.GetWindowPlacement(self.hwnd)
        return tup[1] == win32con.SW_SHOWMINIMIZED

    @property
    def is_foreground(self) -> Union[bool, None]:
        if not self.exists:
            return None

        return win32gui.GetForegroundWindow() == self.hwnd

    @property
    def is_normal(self) -> Union[bool, None]:
        if not self.exists:
            return None

        tup = win32gui.GetWindowPlacement(self.hwnd)
        return tup[1] == win32con.SW_SHOWNORMAL

    @property
    def is_being_dragged(self):
        if not self.exists:
            return None

        thread_info = self.get_thread_info()
        return bool(thread_info.hwndMoveSize) or self.override_drag

    @property
    def is_taskbar_app(self) -> bool:
        if not self.exists:
            return None

        style    : int = win32gui.GetWindowLong(self.hwnd, win32con.GWL_STYLE)
        ex_style : int = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)

        is_app = style & (win32con.WS_OVERLAPPED | win32con.WS_OVERLAPPEDWINDOW)
        is_app_ex = ex_style & (win32con.WS_EX_APPWINDOW | win32con.WS_EX_OVERLAPPEDWINDOW)
        is_tool = ex_style & win32con.WS_EX_TOOLWINDOW
        is_child = win32gui.GetWindow(self.hwnd, win32con.GW_OWNER)

        result = (is_app or is_app_ex) and not is_tool and not is_child
        return bool(result)

    def get_thread_info(self) -> Union[utility.GUITHREADINFO, None]:
        if not self.exists:
            return None

        user32.GetGUIThreadInfo(self.thread_id, byref(self.__thread_info))
        return self.__thread_info

    def validate(self, blacklisted_paths : List[str], whitelisted_paths : List[str]) -> None:
        if not self.is_taskbar_app:
            self.is_valid = False; return

        if utility.path_exists_in_list(self.exe_path, whitelisted_paths):
            self.is_valid = True; return

        self.is_valid = not utility.path_exists_in_list(self.exe_path, blacklisted_paths)

    def on_drag_start(self, pos : Tuple[int, int], is_topmost : bool) -> None:
        if not self.exists:
            return

        if is_topmost and self.drag_rect.collidepoint(pos):
            self.override_drag = True

    def on_drag_stop(self, pos : Tuple[int, int]) -> None:
        if not self.exists:
            return

        self.override_drag = False
        if self.is_foreground and not self.monitor_info.taskbar_rect.collidepoint(pos):
            self.monitor_info = utility.get_monitor_info(self.hwnd)

    def move(self, x : int, y : int, smoothing_factor : float=0.0) -> None:
        if not self.exists or not self.is_normal:
            return

        _rect = self.rect
        _monitor_rect = self.monitor_info.monitor_rect

        dst_pos = utility.lerp((_rect.x, _rect.y), (x, y), 1 - smoothing_factor)
        clamped_width = min(_rect.width, _monitor_rect.width)
        clamped_height = min(_rect.height, _monitor_rect.height)

        try:
            win32gui.MoveWindow(self.hwnd, dst_pos[0], dst_pos[1], clamped_width, clamped_height, 1)

        except win32gui.error as e:
            if e.args[0] == 5:
                print(f"WARNING: No permission to move window: \'{self.title}\' at \'{self.exe_path}\'!")
            else:
                raise e

    def move_random(self, smoothing_factor : float=0.0) -> None:
        if not self.exists or not self.is_normal:
            return

        _rect = self.rect
        _work_area = self.monitor_info.work_area

        pos_x = random.randint(5, max(_work_area.width  - _rect.width  - 5, 5))
        pos_y = random.randint(5, max(_work_area.height - _rect.height - 5, 5))

        self.move(_work_area.x + pos_x, _work_area.y + pos_y, smoothing_factor)

    def move_simplex_random(self, speed : float, smoothing_factor : float=0.0, octaves : int=1, persistence : float=0.5, lacunarity : float=2.0, base : int=0) -> None:
        if not self.exists or not self.is_normal:
            return

        noise_x = noise.snoise2(self.noise_time_x, self.noise_time_x, 
            octaves=octaves, persistence=persistence, lacunarity=lacunarity, base=base)
        noise_y = noise.snoise2(self.noise_time_y, self.noise_time_y, 
            octaves=octaves, persistence=persistence, lacunarity=lacunarity, base=base)

        self.noise_time_x += speed
        self.noise_time_y += speed

        _rect = self.rect
        _work_area = self.monitor_info.work_area

        noise_x = utility.constrain(noise_x, -1, 1, 5, max(_work_area.width  - _rect.width  - 5, 5))
        noise_y = utility.constrain(noise_y, -1, 1, 5, max(_work_area.height - _rect.height - 5, 5))

        self.move(_work_area.x + noise_x, _work_area.y + noise_y, smoothing_factor)
