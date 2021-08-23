__author__ = "Julius Edvardsson"
__version__ = "0.3.1a"
__copyright__ = "Copyright Virus Julius Edvardsson 2021 (©)"
__description__ = "Randomly moves windows using smooth noise."

import argparse, sys

parser = argparse.ArgumentParser(description=__description__)
parser.add_argument('--speed',            '-sp', nargs=1,   type=float, default=[0.225],
                    help='speed when moving a window')

parser.add_argument('--smoothing-factor', '-sm', nargs=1,   type=float, default=[0.85],
                    help='interpolation factor when moving a window')

parser.add_argument('--refresh-rate',     '-r',  nargs=1,   type=float, default=[60.0],
                    help='number of updates per second')

parser.add_argument('--blacklist',        '-b',  nargs='+', type=str,   default=[],
                    help='blacklisted executable paths')

parser.add_argument('--whitelist',        '-w',  nargs='+', type=str,   default=[],
                    help='whitelisted executable paths, overwrites blacklisted paths')

args = parser.parse_args(sys.argv[1:])

import contextlib, time, pyautogui

from lib.windowApp import WindowApp
from lib.mouse import Mouse

with contextlib.redirect_stdout(None):
    from pygame import time as pytime

from os.path import abspath, isabs, relpath
from typing import Dict, List

class Program():
    def __init__(self, args) -> None:
        self.is_running : bool = False
        self.windows : Dict[int, WindowApp] = {}
        self.mouse : Mouse = Mouse()

        self.noise_speed : float = args.speed[0]
        self.smoothing_factor : float = args.smoothing_factor[0]
        self.refresh_rate : float = args.refresh_rate[0]

        self.blacklisted_paths : List[str] = [
            "C:/Windows",
            "C:/Program Files/Windows",
            "C:/Program Files (x86)/Windows"
        ]
        self.blacklisted_paths.extend(args.blacklist)

        self.whitelisted_paths : List[str] = [
            "C:/Windows/explorer.exe",
            "C:/Program Files/WindowsApps"
        ]
        self.whitelisted_paths.extend(args.whitelist)

        self.blacklisted_paths = [abspath(path) if isabs(path) else relpath(path) for path in self.blacklisted_paths]
        self.whitelisted_paths = [abspath(path) if isabs(path) else relpath(path) for path in self.whitelisted_paths]

    def process_window_updates(self) -> None:
        win32_windows : List = pyautogui.getAllWindows()

        for win32_window in win32_windows:
            hwnd = win32_window._hWnd

            new_window = self.windows.get(hwnd, None)
            if new_window is None:
                new_window = WindowApp(hwnd)
                new_window.validate(self.blacklisted_paths, self.whitelisted_paths)

                self.windows[hwnd] = new_window

        windows_to_pop = [window.hwnd for window in self.windows.values() if not window.exists]
        for hwnd in windows_to_pop:
            self.windows.pop(hwnd)

    def process_mouse_updates(self) -> None:
        self.mouse.process_updates(self.windows)

    def main(self, dt : float) -> None:
        for window in self.windows.values():
            if not window.is_valid or window.is_being_dragged:
                continue

            window.move_simplex_random(dt * self.noise_speed, 
                smoothing_factor=self.smoothing_factor, octaves=3, persistence=12, lacunarity=0.4, base=0)

    def run(self) -> None:
        clock = pytime.Clock()

        t_end = 1/self.refresh_rate
        t_start = 0
        delta_time = 1/self.refresh_rate

        self.is_running = True
        while self.is_running:
            t_start = time.perf_counter()

            self.process_window_updates()
            self.process_mouse_updates()
            self.main(delta_time)

            clock.tick(self.refresh_rate)
            t_end = time.perf_counter()
            
            delta_time = t_end - t_start

if __name__ == "__main__":
    program = Program(args)
    program.run()
