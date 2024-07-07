import random
from math import sin, cos, pi
import pygame.draw
from pygame import Vector2
import opensimplex
from numpy import interp


class Segment:
    def __init__(self, position: Vector2, length, angle, phase, width=4):
        self.position = position
        self.length = length
        self.angle = angle
        self.local_angle = angle
        self.parent = None
        self.child = None
        self.end = None
        self.calculate_end()
        opensimplex.random_seed()
        self.phase = phase
        self.width = width
        self.y_off = random.random() * 34786

    def add_child(self, child):
        child.parent = self
        self.child = child
        child.position = Vector2(self.position.x + self.length * cos(self.angle),
                                 self.position.y + self.length * sin(self.angle))

    def calculate_end(self):
        self.end = Vector2(self.position.x + self.length * cos(self.angle),
                           self.position.y + self.length * sin(self.angle))

    def rotate(self):
        min_angle = -0.3
        max_angle = 0.3
        self.local_angle = interp(opensimplex.noise2(self.phase, self.y_off), [-1, 1], [max_angle, min_angle])
        self.phase += 0.03

    def update(self):
        self.angle = self.local_angle
        if self.parent is not None:
            self.position = self.parent.end
            self.angle += self.parent.angle
        else:
            self.angle -= pi * 0.5
        self.calculate_end()

    def show(self, surface):
        width = max(int(self.width), 1)
        pygame.draw.line(surface, (255, 255, 0), self.position, self.end, width)

    @staticmethod
    def map(value, min1, max1, min2, max2):
        return min2 + (value - min1) * (max2 - min2) / (max1 - min1)
