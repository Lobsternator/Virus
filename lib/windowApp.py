import contextlib, random, noise, win32con, win32gui

with contextlib.redirect_stdout(None):
    from pygame import rect as pyrect

from . import utility
from typing import List, Tuple, Union

class WindowApp():
    def __init__(self, hwnd : int) -> None:
        self.hwnd = hwnd
        self.exe_path = utility.get_window_executable_path(self.hwnd)
        self.monitor_info = utility.get_monitor_info(self.hwnd)
        self.is_valid = False
        self.is_being_dragged = False

        random_sample = random.sample(range(0, 1000), 2)
        self.noise_time_x = random_sample[0]
        self.noise_time_y = random_sample[1]

    @property
    def title(self) -> Union[str, None]:
        if not win32gui.IsWindow(self.hwnd):
            return None

        return win32gui.GetWindowText(self.hwnd)

    @property
    def rect(self) -> Union[pyrect.Rect, None]:
        if not win32gui.IsWindow(self.hwnd):
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

    @property
    def is_taskbar_app(self) -> bool:
        if not win32gui.IsWindow(self.hwnd):
            return None

        style    : int = win32gui.GetWindowLong(self.hwnd, win32con.GWL_STYLE)
        ex_style : int = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)

        is_app = style & (win32con.WS_OVERLAPPED | win32con.WS_OVERLAPPEDWINDOW)
        is_app_ex = ex_style & (win32con.WS_EX_APPWINDOW | win32con.WS_EX_OVERLAPPEDWINDOW)
        is_tool = ex_style & win32con.WS_EX_TOOLWINDOW
        is_child = win32gui.GetWindow(self.hwnd, win32con.GW_OWNER)

        result = (is_app or is_app_ex) and not is_tool and not is_child
        return bool(result)

    def validate(self, blacklisted_paths : List[str], whitelisted_paths : List[str]) -> None:
        if self.exe_path is None or self.monitor_info is None:
            self.is_valid = False; return

        if not self.is_taskbar_app:
            self.is_valid = False; return

        if utility.path_exists_in_list(self.exe_path, whitelisted_paths):
            self.is_valid = True; return

        self.is_valid = not utility.path_exists_in_list(self.exe_path, blacklisted_paths)

    def on_mouse_down(self, pos : Tuple[int, int], is_topmost : bool) -> None:
        if not win32gui.IsWindow(self.hwnd):
            return

        if is_topmost and self.drag_rect.collidepoint(pos):
            self.is_being_dragged = True

    def on_mouse_up(self, pos : Tuple[int, int]) -> None:
        if not win32gui.IsWindow(self.hwnd):
            return

        self.is_being_dragged = False

        if self.is_foreground and self.drag_rect.collidepoint(pos):
            self.monitor_info = utility.get_monitor_info(self.hwnd)

    def move(self, x : int, y : int, smoothing_factor : float=0.0) -> None:
        if not win32gui.IsWindow(self.hwnd) or not self.is_normal:
            return

        _rect = self.rect
        dst_pos = utility.lerp((_rect.x, _rect.y), (x, y), 1 - smoothing_factor)

        try:
            win32gui.MoveWindow(self.hwnd, dst_pos[0], dst_pos[1], _rect.width, _rect.height, 1)

        except win32gui.error as e:
            if e.args[0] == 5:
                print(f"WARNING: No permission to move window: \'{self.title}\' at \'{self.exe_path}\'!")
            else:
                raise e

    def move_random(self, smoothing_factor : float=0.0) -> None:
        if not win32gui.IsWindow(self.hwnd) or not self.is_normal:
            return

        _rect = self.rect
        _work_area = self.monitor_info.work_area

        pos_x = random.randint(5, max(_work_area.width  - _rect.width  - 5, 5))
        pos_y = random.randint(5, max(_work_area.height - _rect.height - 5, 5))

        self.move(_work_area.x + pos_x, _work_area.y + pos_y, smoothing_factor)

    def move_simplex_random(self, speed : float, smoothing_factor : float=0.0, octaves : int=1, persistence : float=0.5, lacunarity : float=2.0, base : int=0) -> None:
        if not win32gui.IsWindow(self.hwnd) or not self.is_normal:
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
