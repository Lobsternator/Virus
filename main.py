import sys, contextlib, pyautogui, time
import lib.utility as utility
from lib.windowApp import WindowApp
with contextlib.redirect_stdout(None):
    from pygame import time as pytime
from os.path import abspath, relpath, isabs
from typing import Dict, List

windows : Dict[int, "WindowApp"] = {}

NOISE_SPEED = 0.1
if len(sys.argv) > 1:
    NOISE_SPEED = float(sys.argv[1])

REFRESH_RATE = 60
if len(sys.argv) > 2:
    REFRESH_RATE = float(sys.argv[2])

BLACKLISTED_PATHS = [
    "C:/Windows",
    "C:/Program Files/Windows",
    "C:/Program Files (x86)/Windows"
]
WHITELISTED_PATHS = [
    "C:/Windows/explorer.exe"
]
if len(sys.argv) > 3:
    BLACKLISTED_PATHS.extend(sys.argv[3:])

BLACKLISTED_PATHS = [abspath(path) if isabs(path) else relpath(path) for path in BLACKLISTED_PATHS]
WHITELISTED_PATHS = [abspath(path) if isabs(path) else relpath(path) for path in WHITELISTED_PATHS]

def process_window_updates() -> None:
    win32_windows : List = pyautogui.getAllWindows()

    for win32_window in win32_windows:
        new_window = windows.get(win32_window._hWnd, None)

        if new_window is None:
            hwnd = win32_window._hWnd
            exe_path = utility.get_window_executable_path(win32_window)
            monitor_info = utility.get_monitor_info(hwnd, exe_path)
            
            new_window = WindowApp(hwnd, exe_path, monitor_info)
            new_window.validate(BLACKLISTED_PATHS, WHITELISTED_PATHS)

            windows[hwnd] = new_window

    windows_to_pop = []
    for hwnd in windows.keys():
        found_window = len([w for w in win32_windows if w._hWnd == hwnd]) > 0

        if not found_window:
            windows_to_pop.append(hwnd)

    for hwnd in windows_to_pop:
        windows.pop(hwnd)

def main(dt : float) -> None:
    for window in windows.values():
        if not window.valid:
            continue

        window.move_perlin_random(dt * NOISE_SPEED, octaves=4, persistence=5, lacunarity=1, base=15)

if __name__ == "__main__":
    clock = pytime.Clock()

    t = 1/REFRESH_RATE
    last_t = 0
    delta_time = 1/REFRESH_RATE
    
    while True:
        delta_time = t - last_t
        last_t = time.time()

        process_window_updates()
        main(delta_time)

        clock.tick(REFRESH_RATE)
        t = time.time()
