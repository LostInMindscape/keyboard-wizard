import math

class Vec2:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


    def rotated(self, angle: float) -> Vec2:
        s: float = math.sin(angle)
        c: float = math.cos(angle)

        return Vec2(
            self.x * c - self.y * s,
            self.x * s + self.y * c
        )


    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)


    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)


    def __mul__(self, other: float) -> Vec2:
        return Vec2(
            self.x * other,
            self.y * other
        )