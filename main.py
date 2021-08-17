import sys, time, contextlib
import lib.utility as utility
from lib.windowApp import WindowApp
with contextlib.redirect_stdout(None):
    from pygame import time as pytime
from os.path import abspath, relpath, isabs
from typing import Dict

windows : Dict[int, "WindowApp"] = {}

REFRESH_RATE = 1
if len(sys.argv) > 1:
    REFRESH_RATE = float(sys.argv[1])

BLACKLISTED_PATHS = [
    "C:/Windows",
    "C:/Program Files/Windows",
    "C:/Program Files (x86)/Windows"
]
WHITELISTED_PATHS = [
    "C:/Windows/explorer.exe",
    "C:/Program Files/WindowsApps"
]
if len(sys.argv) > 2:
    BLACKLISTED_PATHS.extend(sys.argv[2:])

BLACKLISTED_PATHS = [abspath(path) if isabs(path) else relpath(path) for path in BLACKLISTED_PATHS]
WHITELISTED_PATHS = [abspath(path) if isabs(path) else relpath(path) for path in WHITELISTED_PATHS]

def main() -> None:    
    for window in windows.values():
        if not window.valid:
            continue

        window.move_random()

if __name__ == "__main__":
    clock = pytime.Clock()

    t = 1/REFRESH_RATE
    last_t = 0
    delta_time = 1/REFRESH_RATE
    
    while True:
        delta_time = t - last_t
        last_t = time.time()
        
        utility.process_window_updates(windows, BLACKLISTED_PATHS, WHITELISTED_PATHS)
        main()

        clock.tick(REFRESH_RATE)
        t = time.time()
