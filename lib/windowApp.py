from typing import List

def path_exists_in_list(path : str, path_list : List[str]) -> bool:
    return any([path.find(listed_path) != -1 for listed_path in path_list])

class WindowApp():
    def __init__(self, title : str, hwnd : int, exe_path : str) -> None:
        self.hwnd = hwnd
        self.exe_path = exe_path
        self.valid = False
        self.title = title

    def validate(self, blacklisted_paths : List[str], whitelisted_paths : List[str]) -> None:
        if self.exe_path is None or self.title == '':
            self.valid = False; return
            
        if path_exists_in_list(self.exe_path, whitelisted_paths):
            self.valid = True; return

        self.valid = not path_exists_in_list(self.exe_path, blacklisted_paths)
