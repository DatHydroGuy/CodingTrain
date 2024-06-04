import ctypes
import math

import pygame
from pygame._sdl2 import Window


class HeartCurve:
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
        angle = 0
        incr = math.pi / 100
        r = 15
        verts = []

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))
            x = 16 * r * math.pow(math.sin(angle), 3) + self.screen_width / 2
            y = -r * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle)) + self.screen_height / 2.4
            if angle <= math.pi * 2:
                verts.append((x, y))
            if len(verts) < 2:
                verts.append((x, y))
            if len(verts) < 3:
                verts.append((x, y))
                verts.append((x, y))

            # render
            # pygame.draw.lines(self.screen, (150, 0, 100), True, verts, 1)
            pygame.draw.polygon(self.screen, (150, 0, 100), verts, 0)
            pygame.draw.lines(self.screen, (255, 255, 255), False, verts, 8)

            pygame.display.set_caption(f"{self.__clock.get_fps()}")
            pygame.display.update()

            angle += incr
            if angle > math.pi * 2:
                angle = 0
                # verts.clear()

            self.__clock.tick(60)
