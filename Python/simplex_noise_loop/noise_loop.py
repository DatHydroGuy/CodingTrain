from math import cos, sin
from random import uniform

import opensimplex
from numpy import interp


class NoiseLoop:
    def __init__(self, noise_space_diameter):
        self.diameter = noise_space_diameter
        opensimplex.random_seed()
        self.noise_delta = 0.2
        self.noise_space_x = uniform(0, 1000000)
        self.noise_space_y = uniform(0, 1000000)

    def value(self, angle, min_value, max_value):
        noise_space_x = interp(self.noise_delta * cos(angle), [-1, 1], [0, self.diameter])
        noise_space_y = interp(self.noise_delta * sin(angle), [-1, 1], [0, self.diameter])
        return interp(opensimplex.noise2(noise_space_x + self.noise_space_x, noise_space_y + self.noise_space_y),
                      [-1, 1], [min_value, max_value])
