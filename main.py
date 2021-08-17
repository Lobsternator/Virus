import sys, time, contextlib
import lib.utility as utility
from lib.windowApp import WindowApp
with contextlib.redirect_stdout(None):
    from pygame import time as pytime
from os.path import abspath, relpath, isabs
from typing import Dict

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
        
        utility.process_window_updates(windows, BLACKLISTED_PATHS, WHITELISTED_PATHS)
        main(delta_time)

        clock.tick(REFRESH_RATE)
        t = time.time()
