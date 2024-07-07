import math
from math import sin, cos
import pygame.draw
from pygame import Vector2


class Segment:
    def __init__(self, position: Vector2, length, angle, width=4):
        self.position = position
        self.length = length
        self.angle = angle
        self.parent = None
        self.child = None
        self.end = None
        self.calculate_end()
        self.width = width

    def add_child(self, child):
        child.parent = self
        self.child = child
        #child.follow(self.position.x, self.position.y)  # child.position = self.get_segment_end_location()

    def calculate_end(self):
        self.end = self.get_segment_end_location()

    def get_segment_end_location(self):
        return Vector2(self.position.x + self.length * cos(self.angle),
                       self.position.y + self.length * sin(self.angle))

    def follow(self, target_x, target_y):
        target = Vector2(target_x, target_y)
        direction = target - self.position
        self.angle = math.atan2(direction.y, direction.x)
        direction = direction.clamp_magnitude(self.length)
        direction *= -1
        self.position = target + direction

    def update(self):
        self.calculate_end()

    def show(self, surface):
        width = max(int(self.width), 1)
        pygame.draw.line(surface, (255, 255, 0), self.position, self.end, width)
