import ctypes
from math import sqrt, fabs

import numpy as np
import pygame
from pygame import pixelcopy
from pygame._sdl2 import Window


class Mandelbrot:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 800  # user32.GetSystemMetrics(0)
        self.screen_height = 600  # user32.GetSystemMetrics(1)

        pygame.init()
        pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)
        self.pg_window = Window.from_display_module()

    def start(self) -> None:
        reds = []
        yellows = []
        whites = []
        for i in range(64):
            reds.append([i * 4, 0, 0])
            yellows.append([255, i * 4, 0])
            whites.append([255, 255, i * 4])
        whites.append([255, 255, 255])

        col_map = reds + yellows + whites
        col_map_len = len(col_map)
        pix_arr = np.array([[[51, 51, 51] for _ in range(self.screen_height)] for _ in range(self.screen_width)],
                           dtype=np.uint8)

        max_iterations = 100
        divergence_threshold = 16

        self.screen.fill((0, 0, 0))

        while 1:
            self.__clock.tick(10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            for x in range(self.screen_width):
                for y in range(self.screen_height):
                    z_real = np.interp(x, [0, self.screen_width], [-2.5, 1.5])
                    z_imag = np.interp(y, [0, self.screen_height], [-1.5, 1.5])

                    c_real = z_real
                    c_imag = z_imag
                    num_iterations = 0

                    while num_iterations < max_iterations:
                        z_squared_real = z_real * z_real - z_imag * z_imag
                        z_squared_imag = 2 * z_real * z_imag

                        z_real = z_squared_real + c_real
                        z_imag = z_squared_imag + c_imag

                        if fabs(z_real + z_imag) > divergence_threshold:
                            break

                        num_iterations += 1

                    if num_iterations == max_iterations:
                        colour = [0, 0, 0]
                    else:
                        normalised_iterations = np.interp(num_iterations, [0, max_iterations], [0, 1])
                        colour = col_map[int(np.interp(sqrt(normalised_iterations), [0, 1], [0, col_map_len]))]

                    pix_arr[x][y] = colour

            # render
            pixelcopy.array_to_surface(self.screen, pix_arr)  # fast copy colour array to screen

            pygame.display.update()
