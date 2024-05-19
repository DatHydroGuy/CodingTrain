from pygame import Vector2


class Blob:
    def __init__(self, x, y, r, vx, vy):
        self.pos = Vector2(x, y)
        self.vel = Vector2(vx, vy)
        self.r = r
