import pyautogui, random, win32gui, win32con
from typing import List, Union

SCREEN_SIZE = pyautogui.size()

def path_exists_in_list(path : str, path_list : List[str]) -> bool:
    return any([path.find(listed_path) != -1 for listed_path in path_list])

class WindowApp():
    def __init__(self, hwnd : int, exe_path : str) -> None:
        self.hwnd = hwnd
        self.exe_path = exe_path
        self.valid = False

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
        if self.exe_path is None or self.title == '':
            self.valid = False; return
            
        if path_exists_in_list(self.exe_path, whitelisted_paths):
            self.valid = True; return

        self.valid = not path_exists_in_list(self.exe_path, blacklisted_paths)

    def move_random(self) -> None:
        if not win32gui.IsWindow(self.hwnd) or not self.is_normal:
            return

        pos_x = random.randint(0, SCREEN_SIZE[0] - self.width)
        pos_y = random.randint(0, SCREEN_SIZE[1] - self.height)

        try:
            win32gui.MoveWindow(self.hwnd, pos_x, pos_y, int(self.width), int(self.height), 1)

        except Exception as e:
            if e.args[0] == 5:
                print(f"WARNING: No permission to move window {self.title}")
            else:
                raise e
