import ctypes
from math import sin, cos, pi
import opensimplex
import pygame
from pygame._sdl2 import Window
from numpy import interp


class PolarSimplexNoiseLoop:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 800  # user32.GetSystemMetrics(0)
        self.screen_height = 600  # user32.GetSystemMetrics(1)

        pygame.init()

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)
        self.pg_window = Window.from_display_module()

    def start(self) -> None:
        incr = pi / 50
        opensimplex.random_seed()
        phase = 0
        noise_space_z = 0

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))

            noise_radius = 1.5
            angle = 0
            verts = []
            noise_max = 5
            while angle < pi * 2:
                noise_space_x = interp(noise_radius * cos(angle + phase), [-1, 1], [0, noise_max])
                noise_space_y = interp(noise_radius * sin(angle + phase), [-1, 1], [0, noise_max])
                r = interp(opensimplex.noise3(noise_space_x, noise_space_y, noise_space_z), [-1, 1], [100, 200])

                x = r * cos(angle) + self.screen_width / 2
                y = r * sin(angle) + self.screen_height / 2
                verts.append((x, y))
                angle += incr

            # render
            pygame.draw.lines(self.screen, (255, 255, 255), True, verts, 1)

            # phase += 0.01
            noise_space_z += 0.01

            pygame.display.set_caption(f"{self.__clock.get_fps()}")
            pygame.display.update()
            self.__clock.tick(60)

    @staticmethod
    def remap_value(x, min_old, max_old, min_new, max_new):
        """
        Remaps a value from one range to another.

        Parameters:
        x (float): The value to remap.
        min_old (float): Minimum value of the original range.
        max_old (float): Maximum value of the original range.
        min_new (float): Minimum value of the new range.
        max_new (float): Maximum value of the new range.

        Returns:
        float: The remapped value.
        """
        return (x - min_old) / (max_old - min_old) * (max_new - min_new) + min_new
