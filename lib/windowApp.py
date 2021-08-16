class WindowApp():
    def __init__(self, win32_window) -> None:
        self.title = win32_window.title
        self.hwnd = win32_window._hWnd
