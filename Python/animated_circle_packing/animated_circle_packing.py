import ctypes
from math import hypot, fabs
from random import uniform

import pygame
from pygame import Vector2
from pygame._sdl2 import Window

from circle import Circle


class AnimatedCirclePacking:
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

    def start(self) -> None:
        circles = []

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))
            c = self.new_circle(circles)
            if c is not None:
                circles.append(c)

            # render
            for circle in circles:
                if circle.growing:
                    if circle.edges(self.screen_width, self.screen_height):
                        circle.growing = False
                    else:
                        for other in circles:
                            if other is not circle:
                                dist = hypot(fabs(circle.pos.x - other.pos.x), fabs(circle.pos.y - other.pos.y))
                                if dist < circle.radius + other.radius:
                                    circle.growing = False
                                    break

                circle.draw(self.screen)
                circle.grow()

            self.__clock.tick(60)
            pygame.display.flip()

    def new_circle(self, circles):
        x = uniform(0, self.screen_width)
        y = uniform(0, self.screen_height)

        valid = True
        for circle in circles:
            dist = hypot(fabs(x - circle.pos.x), fabs(y - circle.pos.y))
            if dist < circle.radius:
                valid = False
                break

        if valid:
            return Circle(Vector2(x, y), 1)
        else:
            return None
