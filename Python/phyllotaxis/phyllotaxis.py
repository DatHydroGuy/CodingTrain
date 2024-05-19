import ctypes
import math
from colorsys import hls_to_rgb

import pygame
from pygame import Color
from pygame._sdl2 import Window


class Phyllotaxis:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)

        pygame.init()
        pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)
        self.pg_window = Window.from_display_module()

    @staticmethod
    def colour_by_hue(hue, lightness=0.5, saturation=1.0):
        r, g, b = hls_to_rgb(hue, lightness, saturation)
        r, g, b = [int(255 * i) for i in (r, g, b)]
        return Color(r, g, b, 255)

    def start(self) -> None:
        n = 0
        c = 8
        self.screen.fill((0, 0, 0))
        half_screen_diagonal = math.hypot(self.screen_width, self.screen_height) / 2.0

        while 1:
            self.__clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            angle = n * math.radians(137.5)
            radius = c * math.sqrt(n)
            x = radius * math.cos(angle) + self.screen_width / 2
            y = radius * math.sin(angle) + self.screen_height / 2
            saturation = math.fabs(half_screen_diagonal - radius) / half_screen_diagonal
            colour = self.colour_by_hue(angle % 360, saturation=saturation)

            # render
            pygame.draw.circle(self.screen, colour, (x, y), 4)

            n += 1
            pygame.display.update()
