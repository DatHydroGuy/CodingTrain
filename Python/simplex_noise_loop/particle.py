from pygame import draw, Color, Surface, SRCALPHA

from noise_loop import NoiseLoop


class Particle:
    def __init__(self):
        self.x_noise = NoiseLoop(5)
        self.y_noise = NoiseLoop(5)
        self.d_noise = NoiseLoop(5)
        self.r_noise = NoiseLoop(5)
        self.g_noise = NoiseLoop(5)
        self.b_noise = NoiseLoop(5)

    def render(self, angle, width, height):
        radius = self.d_noise.value(angle, 10, 40)
        circle = Surface((radius * 2, radius * 2), SRCALPHA)
        x = self.x_noise.value(angle, 0, width - radius)
        y = self.y_noise.value(angle, 0, height - radius)
        red = self.r_noise.value(angle, 50, 255)
        green = 50  # self.g_noise.value(angle, 100, 255)
        blue = self.b_noise.value(angle, 50, 255)
        colour = Color(red, green, blue, 150)
        draw.circle(circle, colour, (radius, radius), radius)
        return circle, x, y
