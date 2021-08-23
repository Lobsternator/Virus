from . import utility

class MonitorInfo():
    def __init__(self, monitor_info : dict) -> None:
        self.monitor_rect = utility.convert_rect(monitor_info.get("Monitor"))
        self.work_area = utility.convert_rect(monitor_info.get("Work"))
