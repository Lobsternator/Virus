import contextlib

with contextlib.redirect_stdout(None):
    from pygame import rect as pyrect

from . import utility

class MonitorInfo():
    def __init__(self, monitor_info : dict) -> None:
        self.monitor_rect = utility.convert_rect(monitor_info.get("Monitor"))
        self.work_area = utility.convert_rect(monitor_info.get("Work"))

        if self.work_area.height < self.monitor_rect.height and self.work_area.y == self.monitor_rect.y:
            # ----- Bottom -----
            taskbar_x = self.work_area.x
            taskbar_y = self.work_area.y + self.work_area.height
            taskbar_width = self.work_area.width
            taskbar_height = self.monitor_rect.height - self.work_area.height

        elif self.work_area.width < self.monitor_rect.width and self.work_area.x == self.monitor_rect.x:
            # ----- Right -----
            taskbar_x = self.work_area.x + self.work_area.width
            taskbar_y = self.work_area.y
            taskbar_width = self.monitor_rect.width - self.work_area.width
            taskbar_height = self.work_area.height

        elif self.work_area.x > self.monitor_rect.x:
            # ----- Left -----
            taskbar_x = self.work_area.x
            taskbar_y = self.work_area.y
            taskbar_width = self.monitor_rect.width - self.work_area.width
            taskbar_height = self.work_area.height

        else:
            # ----- Top -----
            taskbar_x = self.work_area.x
            taskbar_y = self.work_area.y
            taskbar_width = self.work_area.width
            taskbar_height = self.monitor_rect.height - self.work_area.height

        self.taskbar_rect = pyrect.Rect(taskbar_x, taskbar_y, taskbar_width, taskbar_height)
