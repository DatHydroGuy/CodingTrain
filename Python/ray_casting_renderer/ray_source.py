import math
import pygame
from ray import Ray


class RaySource:
    def __init__(self, scr_width, scr_height, render_width):
        self.origin = pygame.Vector2(scr_width / 2, scr_height / 2)
        self.render_width = render_width // 2
        self.azimuth = 0
        self.direction = pygame.Vector2(math.cos(self.azimuth), math.sin(self.azimuth))
        self.rays = []
        for a in range(-self.render_width, self.render_width, 1):
            self.rays.append(Ray(self.origin, math.radians(a)))

    def change_fov(self, new_fov):
        self.render_width = new_fov // 2
        self.update(self.origin.x, self.origin.y)

    def move(self, amount):
        self.origin += amount * 2 * self.direction

    def rotate(self, angle):
        self.azimuth += angle
        self.update(self.origin.x, self.origin.y)

    def intersect(self, surface, boundaries, use_euclidean_distance):
        render_strips = []
        for ray in self.rays:
            closest = None
            curr_min = 999999999
            for boundary in boundaries:
                pt = ray.intersect(boundary)
                if pt:
                    dist = self.origin.distance_to(pt)
                    # Don't use Euclidean distance - it gives a fish-eye lens effect
                    # Use the projection of the ray onto the direction vector of the ray_source
                    # Essentially multiply dist by the cos(ray.direction - self.direction)
                    if not use_euclidean_distance:
                        dot = ray.direction.dot(self.direction)
                        dist *= dot / (ray.direction.magnitude() * self.direction.magnitude())
                    if dist < curr_min:
                        curr_min = dist
                        closest = pt

            if closest is not None:
                pygame.draw.line(surface, pygame.Color(255, 255, 255, 100), self.origin, closest, 1)

            render_strips.append(curr_min)

        return render_strips

    def update(self, x, y):
        self.direction = pygame.Vector2(math.cos(math.radians(self.azimuth)), math.sin(math.radians(self.azimuth)))
        self.origin = pygame.Vector2(x, y)
        self.rays = []
        for a in range(int(self.azimuth - self.render_width), int(self.azimuth + self.render_width), 1):
            self.rays.append(Ray(self.origin, math.radians(a)))

    def show(self, surface):
        pygame.draw.circle(surface, pygame.Color(0, 255, 0), (self.origin.x, self.origin.y), 4)
        for ray in self.rays:
            ray.show(surface)
