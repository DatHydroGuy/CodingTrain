from math import sqrt
import pygame
from numpy import interp


class Marker:
    def __init__(self, pos, magnitude, timestamp):
        self.pos = pos
        self.curr_radius = 0
        mag = sqrt(pow(10, magnitude))
        max_mag = sqrt(pow(10, 10))
        self.final_radius = interp(mag, [0, max_mag], [0, 15])
        self.timestamp = timestamp

    def update(self, global_time):
        if self.timestamp <= global_time < self.timestamp + 5/6:
            self.curr_radius += self.final_radius / (4 / 6)
        elif self.timestamp + 5/6 <= global_time <= self.timestamp + 1:
            self.curr_radius -= self.final_radius / (4/6)

    def show(self, surface):
        pygame.draw.circle(surface, (255, 0, 255), self.pos, self.curr_radius, 0)
