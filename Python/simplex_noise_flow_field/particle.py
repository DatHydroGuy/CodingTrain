import pygame.draw
from pygame import Vector2


class Particle:
    def __init__(self, x, y, screen_width, screen_height):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.width = screen_width
        self.height = screen_height
        self.max_speed = 2
        self.force_multiplier = 1
        self.prev_pos = self.pos.copy()

    def update(self):
        self.prev_pos = self.pos.copy()
        self.vel += self.acc
        self.vel = self.vel.clamp_magnitude(self.max_speed)
        self.pos += self.vel
        self.acc *= 0

    def apply_force(self, force):
        self.acc += force * self.force_multiplier

    def edges(self):
        if self.pos.x > self.width - 1:
            self.pos.x = 0
            self.prev_pos = self.pos.copy()
        if self.pos.x < 0:
            self.pos.x = self.width - 1
            self.prev_pos = self.pos.copy()
        if self.pos.y > self.height - 1:
            self.pos.y = 0
            self.prev_pos = self.pos.copy()
        if self.pos.y < 0:
            self.pos.y = self.height - 1
            self.prev_pos = self.pos.copy()

    def follow(self, force):
        self.apply_force(Vector2(1, 0).rotate_rad(force[0]))

    def show(self, surface):
        # pygame.draw.circle(surface, (200, 200, 255, 1), self.pos, 1)
        pygame.draw.line(surface, (255, 255, 255, 255), self.pos, self.prev_pos)
