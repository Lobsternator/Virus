from .rect import Rect

class MonitorInfo():
    def __init__(self, monitor_rect : Rect, work_rect : Rect) -> None:
        self.monitor_rect = monitor_rect
        self.work_area = work_rect

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

        self.taskbar_rect = Rect(taskbar_x, taskbar_y, taskbar_width, taskbar_height)
