from colorsys import rgb_to_hls
from random import uniform
from math import sin, cos, pi
from config import *
import pygame


class Particle:
    def __init__(self, x, y, color, is_rocket):
        self.pos = pygame.Vector2(x, y)
        self.is_rocket = is_rocket
        self.lifespan = MAX_LIFESPAN
        self.color = color
        self.parent_hue = None

        if is_rocket:
            self.vel = pygame.Vector2(uniform(-MAX_ANGLE, MAX_ANGLE), uniform(-SCREEN_HEIGHT / 50, -SCREEN_HEIGHT / 70))
        else:
            if self.parent_hue is None:
                self.parent_hue = rgb_to_hls(*self.color[:3])[0]
            angle_rad = uniform(0, 2 * pi)
            mult = uniform(1, MAX_BURST_SPEED)
            x = cos(angle_rad) * mult
            y = sin(angle_rad) * mult
            self.vel = pygame.Vector2(x, y)
        self.acc = pygame.Vector2(0, 0)

    def apply_force(self, force):
        self.acc += force

    def done(self):
        return self.lifespan <= 0

    def update(self):
        if not self.is_rocket:
            self.vel *= 0.99
            self.lifespan = max(self.lifespan - LIFESPAN_DECAY_RATE, 0)
        self.pos += self.vel
        self.vel += self.acc
        self.acc = pygame.Vector2(0, 0)

    def draw(self, screen):
        if not self.is_rocket:
            curr_life = self.lifespan / MAX_LIFESPAN
            self.color = colour_by_hue(self.parent_hue + curr_life, curr_life, False)
            r = 2
        else:
            r = 4
        pygame.draw.circle(screen, self.color, self.pos, r)
