import pyautogui

windows = []

class WindowApp():
    def __init__(self, win32_window) -> None:
        self.hwnd = win32_window._hWnd
        windows.append(self)

if __name__ == "__main__":
    for window in pyautogui.getAllWindows():
        WindowApp(window)
