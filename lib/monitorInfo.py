class MonitorInfo():
    def __init__(self, monitor_info : dict) -> None:
        self.monitor_rect = list(monitor_info.get("Monitor"))
        self.monitor_rect[2] -= self.monitor_rect[0]
        self.monitor_rect[3] -= self.monitor_rect[1]
        self.monitor_rect = tuple(self.monitor_rect)

        self.work_area = list(monitor_info.get("Work"))
        self.work_area[2] -= self.monitor_rect[0]
        self.work_area[2] -= self.work_area[0] - self.monitor_rect[0]

        self.work_area[3] -= self.monitor_rect[1]
        self.work_area[3] -= self.work_area[1] - self.monitor_rect[1]
        self.work_area = tuple(self.work_area)
