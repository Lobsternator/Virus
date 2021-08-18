import sys, argparse

parser = argparse.ArgumentParser(description='Randomly moves windows using simpelx noise.')
parser.add_argument('--speed', '-s', type=float, default=0.2,
                    help='speed of the random movement of windows')

parser.add_argument('--refresh-rate', '-r', type=float, default=60.0,
                    help='number of updates per second')

parser.add_argument('--blacklist', '-b', nargs='+', type=str, default=[],
                    help='blacklisted executable paths')

parser.add_argument('--whitelist', '-w', nargs='+', type=str, default=[],
                    help='whitelisted executable paths, overwrites blacklisted paths')

try:
    args = parser.parse_args(sys.argv[1:])
except SystemExit as e:
    if not getattr(sys, 'frozen', False):
        input()

    sys.exit(e.code)

import contextlib, pyautogui, time
import lib.utility as utility
from lib.windowApp import WindowApp
with contextlib.redirect_stdout(None):
    from pygame import time as pytime
from os.path import abspath, relpath, isabs
from typing import Dict, List

windows : Dict[int, WindowApp] = {}

NOISE_SPEED = args.speed
REFRESH_RATE = args.refresh_rate

BLACKLISTED_PATHS = [
    "C:/Windows",
    "C:/Program Files/Windows",
    "C:/Program Files (x86)/Windows"
]
BLACKLISTED_PATHS.extend(args.blacklist)

WHITELISTED_PATHS = [
    "C:/Windows/explorer.exe"
]
WHITELISTED_PATHS.extend(args.whitelist)

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

        window.move_simplex_random(dt * NOISE_SPEED, octaves=3, persistence=12, lacunarity=0.4, base=0)

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
