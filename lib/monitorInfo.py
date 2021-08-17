class MonitorInfo():
    def __init__(self, monitor_info : dict) -> None:
        self.monitor_rect = monitor_info.get("Monitor")
        self.work_area = monitor_info.get("Work")[2:]
