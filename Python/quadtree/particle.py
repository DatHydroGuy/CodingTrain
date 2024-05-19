from random import random, uniform
import pygame


class Particle:
    def __init__(self, scr_width, scr_height):
        self.r = 10
        self.x = random() * (scr_width - 2 * self.r) + self.r
        self.y = random() * (scr_height - 2 * self.r) + self.r
        self.x_vel = uniform(-3, 3)
        self.y_vel = uniform(-2, 2)
        self.highlight = False
        self.w = scr_width
        self.h = scr_height

    def intersects(self, other):
        d = (self.x - other.x) ** 2 + (self.y - other.y) ** 2
        return d < (self.r + other.r) ** 2

    def set_highlight(self, value):
        self.highlight = value

    def move(self):
        self.x += self.x_vel
        if not self.r <= self.x <= self.w - self.r:
            self.x_vel *= -1
        self.y += self.y_vel
        if not self.r <= self.y <= self.h - self.r:
            self.y_vel *= -1

    def render(self, screen):
        if self.highlight:
            col = pygame.color.Color('white')
        else:
            col = pygame.color.Color('dimgrey')
        pygame.draw.circle(screen, col, (self.x, self.y), self.r, 0)
