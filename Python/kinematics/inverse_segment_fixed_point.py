from math import sin, cos, radians
import pygame.draw
from pygame import Vector2


class Segment:
    def __init__(self, position: Vector2, length, width=4):
        self.position = position
        self.length = length
        self.angle = 0
        self.end = None
        self.calculate_end()
        self.width = width

    def constrain_position(self, position: Vector2):
        self.position = position
        self.calculate_end()

    def calculate_end(self):
        self.end = self.get_segment_end_location()

    def get_segment_end_location(self):
        return Vector2(self.position.x + self.length * cos(self.angle),
                       self.position.y + self.length * sin(self.angle))

    def follow(self, target_x, target_y):
        if target_x is None or target_y is None:
            return
        target = Vector2(target_x, target_y)
        direction = target - self.position
        self.angle = radians(direction.as_polar()[1])
        direction = direction.normalize() * self.length
        direction *= -1
        self.position = target + direction

    def update(self):
        self.calculate_end()

    def show(self, surface):
        width = max(int(self.width), 1)
        pygame.draw.line(surface, (255, 255, 0), self.position, self.end, width)
