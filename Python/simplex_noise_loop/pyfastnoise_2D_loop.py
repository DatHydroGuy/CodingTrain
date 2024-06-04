import ctypes

import numpy as np
import pygame
import pyfastnoisesimd as fns
from pygame import pixelcopy
from pygame._sdl2 import Window
from math import sin, cos


class Randomness:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 800  # user32.GetSystemMetrics(0)
        self.screen_height = 600  # user32.GetSystemMetrics(1)
        self.num_frames = 250

        pygame.init()
        pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)
        self.pg_window = Window.from_display_module()

    def start(self) -> None:
        seed = np.random.randint(2 ** 31)
        num_threads = 8
        # shape = [self.screen_width, self.screen_height, self.screen_width, self.screen_width]

        simplex = fns.Noise(seed=seed, numWorkers=num_threads)
        simplex.frequency = 0.02
        simplex.noiseType = fns.NoiseType.Simplex
        simplex.fractal.octaves = 4
        simplex.fractal.lacunarity = 2.1
        simplex.fractal.gain = 0.45
        simplex.perturb.perturbType = fns.PerturbType.NoPerturb
        # result = simplex.genFromCoords(shape)       # generate array of Simplex noise values in the range -1 to 1
        # result += 1                             # translate noise range to be 0 to 2
        # result *= 127.5                         # translate noise range to be 0 to 255 (for generating colours)

        idx = 0

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))

            percent = idx / self.num_frames
            angle = np.interp(percent, [0, 1], [0, 2 * np.pi])
            u_off = np.interp(cos(angle), [-1, 1], [0, self.screen_height])   # 3rd dimension of noise space
            v_off = np.interp(sin(angle), [-1, 1], [0, self.screen_height])   # 4th dimension of noise space

            u_off = int(u_off)
            v_off = int(v_off)

            for y in range(0, self.screen_height):
                for x in range(0, self.screen_width):
                    result = simplex.genFromCoords(np.ndarray([x, y, u_off, v_off]))  # generate array of Simplex noise values in the range -1 to 1
                    a = 1

            test = result[:, :, u_off, v_off]            # take a 2D slice of the 4D noise array
            test = np.repeat(test[:, :, np.newaxis], 3, axis=2)     # repeat each value 3 times (for RGB colour)
            test = test.astype(np.uint8)        # convert to integers (since that's what pygame's colours expect)

            idx += 1
            if idx == self.num_frames:
                idx = 0

            # render
            pixelcopy.array_to_surface(self.screen, test)   # fast copy colour array to screen

            pygame.display.update()

            self.__clock.tick(60)
