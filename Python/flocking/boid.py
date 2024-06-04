from math import hypot
from random import uniform

from pygame import Vector2, draw


class Boid:
    def __init__(self, width, height):
        self.position = Vector2(uniform(0, width), uniform(0, height))
        self.velocity = Vector2(uniform(-1.5, 1.5), uniform(-1.5, 1.5))
        while self.velocity.magnitude() < 2:
            self.velocity = Vector2(uniform(-4, 4), uniform(-4, 4))
        self.acceleration = Vector2(0, 0)
        self.max_force = 0.5
        self.max_speed = 4

    def edges(self, width, height):
        if self.position.x > width:
            self.position.x = 0
        if self.position.x < 0:
            self.position.x = width
        if self.position.y > height:
            self.position.y = 0
        if self.position.y < 0:
            self.position.y = height

    def flock(self, boids):
        alignment = self.align(boids)
        cohesion = self.cohesion(boids)
        separation = self.separation(boids)
        self.acceleration = alignment
        self.acceleration += cohesion
        self.acceleration += separation

    def align(self, boids):
        perception_radius = 50
        steering_force = Vector2(0, 0)
        count = 0
        for boid in boids:
            dist = hypot(boid.position.x - self.position.x, boid.position.y - self.position.y) - 10
            if boid != self and dist < perception_radius:
                steering_force += boid.velocity
                count += 1
        if count > 0:
            steering_force /= count
            steering_force = steering_force.normalize() * self.max_speed
            steering_force -= self.velocity
            steering_force = steering_force.clamp_magnitude(self.max_force * 1.2)
        return steering_force

    def cohesion(self, boids):
        perception_radius = 50
        steering_force = Vector2(0, 0)
        count = 0
        for boid in boids:
            dist = hypot(boid.position.x - self.position.x, boid.position.y - self.position.y) - 10
            if boid != self and dist < perception_radius:
                steering_force += boid.position
                count += 1
        if count > 0:
            steering_force /= count
            steering_force -= self.position
            steering_force = steering_force.normalize() * self.max_speed
            steering_force -= self.velocity
            steering_force = steering_force.clamp_magnitude(self.max_force)
        return steering_force

    def separation(self, boids):
        perception_radius = 50
        steering_force = Vector2(0, 0)
        count = 0
        for boid in boids:
            dist = hypot(boid.position.x - self.position.x, boid.position.y - self.position.y) - 10
            if boid != self and dist < perception_radius:
                difference = Vector2(self.position - boid.position)
                difference /= dist
                steering_force += difference
                count += 1
        if count > 0:
            steering_force /= count
            steering_force = steering_force.normalize() * self.max_speed
            steering_force -= self.velocity
            steering_force = steering_force.clamp_magnitude(self.max_force * 1.4)
        return steering_force

    def update(self):
        self.position += self.velocity
        self.velocity += self.acceleration
        self.velocity.clamp_magnitude(self.max_speed)
        self.acceleration = Vector2(0, 0)

    def show(self, surface):
        draw.circle(surface, (255, 255, 255), self.position, 5)
        draw.line(surface, (255, 255, 255), self.position, self.position + self.velocity * 3, 1)
