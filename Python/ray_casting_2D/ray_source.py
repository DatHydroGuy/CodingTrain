import math
import pygame
from ray import Ray


class RaySource:
    def __init__(self, scr_width, scr_height):
        self.origin = pygame.Vector2(scr_width / 2, scr_height / 2)
        self.rays = []

    def intersect(self, surface, boundaries):
        for ray in self.rays:
            closest = None
            curr_min = 999999999
            for boundary in boundaries:
                pt = ray.intersect(boundary)
                if pt:
                    dist = self.origin.distance_to(pt)
                    if dist < curr_min:
                        curr_min = dist
                        closest = pt

            if closest is not None:
                pygame.draw.line(surface, pygame.Color(255, 255, 255, 100), self.origin, closest, 1)

    def update(self, x, y):
        self.origin = pygame.Vector2(x, y)
        self.rays = []
        for a in range(0, 360, 1):
            self.rays.append(Ray(self.origin, math.radians(a)))

    def show(self, surface):
        pygame.draw.circle(surface, pygame.Color(0, 255, 0), (self.origin.x, self.origin.y), 4)
        for ray in self.rays:
            ray.show(surface)
