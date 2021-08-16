import lib.utility as utility
from lib.windowApp import WindowApp
from pygame import time as pytime
from typing import Dict

windows : Dict[int, "WindowApp"] = {}
REFRESH_RATE = 2

if __name__ == "__main__":
    utility.process_window_updates(windows)

    clock = pytime.Clock()
    t = 0
    last_t = 0
    delta_time = 1/REFRESH_RATE
    
    while True:
        utility.process_window_updates(windows)

        print(len(windows))

        clock.tick_busy_loop(REFRESH_RATE)
