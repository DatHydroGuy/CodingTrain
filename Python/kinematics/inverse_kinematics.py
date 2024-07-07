import ctypes
from math import radians

import pygame
from pygame import Vector2
from inverse_segment import Segment


class InverseKinematics:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 800  # user32.GetSystemMetrics(0)
        self.screen_height = 600  # user32.GetSystemMetrics(1)

        pygame.init()
        pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)

    def start(self) -> None:
        segment_length = 100
        segment_width = 14
        tentacle = Segment(Vector2(self.screen_width / 2, self.screen_height / 2), segment_length, radians(-45), segment_width)
        seg2 = Segment(tentacle.end, segment_length, radians(10))
        tentacle.add_child(seg2)
        mouse_x = seg2.position.x
        mouse_y = seg2.position.y

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.MOUSEMOTION:
                    mouse_x, mouse_y = event.pos

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))

            seg2.follow(mouse_x, mouse_y)
            seg2.update()
            tentacle.follow(seg2.position.x, seg2.position.y)
            tentacle.update()

            # render
            seg2.show(self.screen)
            tentacle.show(self.screen)

            self.__clock.tick(60)
            pygame.display.update()
