import math
import pygame


class Ray:
    def __init__(self, position, direction):
        self.origin = position
        self.direction = pygame.Vector2(math.cos(direction), math.sin(direction))

    def look_at(self, x, y):
        self.direction.x = x - self.origin.x
        self.direction.y = y - self.origin.y
        self.direction.normalize()

    def intersect(self, boundary):
        x1 = boundary.a.x
        y1 = boundary.a.y
        x2 = boundary.b.x
        y2 = boundary.b.y

        x3 = self.origin.x
        y3 = self.origin.y
        x4 = self.origin.x + self.direction.x
        y4 = self.origin.y + self.direction.y

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        if 0 <= t <= 1 and 0 <= u:
            return pygame.Vector2(x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        else:
            return None

    def show(self, surface):
        # pygame.draw.line(surface, pygame.Color(255, 255, 255, 100), self.origin, self.origin + self.direction * 10, 1)
        pass
