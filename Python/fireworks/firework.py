from random import random
from config import *
from particle import Particle


class Firework:
    def __init__(self, max_x, max_y):
        self.color = colour_by_hue(random(), 1.0, True)
        launch_bounds = random() * (max_x - MAX_ANGLE * 50) + MAX_ANGLE * 25
        self.firework = Particle(launch_bounds, max_y, self.color, True)
        self.exploded = False
        self.particles = []

    def explode(self):
        for i in range(NUM_PARTICLES_IN_BURST):
            self.particles.append(Particle(self.firework.pos.x, self.firework.pos.y, self.color, False))

    def done(self):
        return self.exploded and len(self.particles) == 0

    def update(self, gravity):
        if not self.exploded:
            self.firework.apply_force(gravity)
            self.firework.update()

            if self.firework.vel.y >= 0:
                self.exploded = True
                self.explode()

        for particle in self.particles[::-1]:
            particle.apply_force(gravity)
            particle.update()
            if particle.done():
                self.particles.remove(particle)

    def draw(self, screen):
        if not self.exploded:
            self.firework.draw(screen)
        for particle in self.particles:
            particle.draw(screen)
