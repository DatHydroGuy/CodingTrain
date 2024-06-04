import ctypes
import pygame
from pygame._sdl2 import Window

from boid import Boid


class Flocking:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)

        pygame.init()

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)
        self.pg_window = Window.from_display_module()

    def start(self) -> None:
        flock = []

        for _ in range(200):
            flock.append(Boid(self.screen_width, self.screen_height))

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))
            flock_copy = flock.copy()

            # render
            for idx, boid in enumerate(flock_copy):
                boid.edges(self.screen_width, self.screen_height)
                boid.flock(flock)
                flock[idx].update()
                flock[idx].show(self.screen)

            pygame.display.set_caption(f"{self.__clock.get_fps()}")
            pygame.display.update()

            self.__clock.tick(60)
