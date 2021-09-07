from typing import Tuple

class Rect():
    def __init__(self, x : int, y : int, width : int, height : int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains_point(self, point : Tuple[int, int]) -> bool:
        return (
            point[0] >= self.x and 
            point[1] >= self.y and 
            point[0] < self.x + self.width and 
            point[1] < self.y + self.height
        )
