import ctypes
from math import pi  # , sin, cos
from random import uniform

import numpy as np
import pygame
import pyfastnoisesimd as fns
# from pygame import pixelcopy

from simplex_noise_flow_field.particle import Particle


class PyFastNoise2d:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)

        pygame.init()
        pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.window = pygame.display.set_mode(window_size)#, pygame.DOUBLEBUF, 32)
        self.screen = pygame.Surface(window_size, pygame.SRCALPHA)

    def start(self) -> None:
        seed = np.random.randint(2 ** 31)
        num_threads = 8

        simplex = fns.Noise(seed=seed, numWorkers=num_threads)
        simplex.frequency = min(self.screen_width, self.screen_height) / 20000.0
        simplex.noiseType = fns.NoiseType.Simplex
        simplex.fractal.octaves = 4
        simplex.fractal.lacunarity = 2.1
        simplex.fractal.gain = 0.45
        simplex.perturb.perturbType = fns.PerturbType.NoPerturb

        scl = 20
        cols = self.screen_width // scl
        cols -= cols % np.dtype(np.float32).itemsize
        rows = self.screen_height // scl
        rows -= rows % np.dtype(np.float32).itemsize
        # shape = [self.screen_width, self.screen_height, 1]
        shape = [cols, rows, 1]
        idx = 0
        frames = 0

        particles = []
        for _ in range(10000):
            particles.append(Particle(uniform(0, self.screen_width),
                                      uniform(0, self.screen_height),
                                      self.screen_width,
                                      self.screen_height))

        self.screen.fill((0, 0, 0, 255))
        # self.window.fill((200, 200, 200, 255))

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0, 1))
            # self.window.fill((0, 0, 0, 255))

            # generate array of Simplex noise values in the range -pi to pi
            result = simplex.genAsGrid(shape, start=[0, 0, idx])
            test = result * pi
            # result += 1  # translate noise range to be 0 to 2
            # result *= 127.5  # translate noise range to be 0 to 255 (for generating colours)
            # test = np.repeat(result[:, :, :], 3, axis=2)     # repeat each value 3 times (for RGB colour)
            # test = np.repeat(test[:, :, :], scl, axis=0)     # repeat each x value scl times
            # test = np.repeat(test[:, :, :], scl, axis=1)     # repeat each y value scl times
            # test = test.astype(np.uint8)        # convert to integers (since that's what pygame's colours expect)

            frames += 1
            if frames == 20:
                frames = 0
                idx += 1
                # self.screen.fill((0, 0, 0, 1))
                print(f"FPS: {self.__clock.get_fps()}")
            # idx += 1

            # render
            # pixelcopy.array_to_surface(self.screen, test)   # fast copy array to screen
            # for x in range(cols):
            #     for y in range(rows):
            #         pygame.draw.line(self.screen, (255, 255, 255, 100),
            #                          (x * scl, y * scl),
            #                          (x * scl + cos(test[x, y]) * scl,
            #                           y * scl + sin(test[x, y]) * scl),
            #                          1)

            for particle in particles:
                particle.update()
                particle.edges()
                particle.follow(test[int(particle.pos.x // scl), int(particle.pos.y // scl)])
                particle.show(self.screen)

            self.window.blit(self.screen, (0, 0))
            pygame.display.flip()
            # pygame.display.set_caption(f"FPS: {self.__clock.get_fps()}")
            self.__clock.tick(60)
