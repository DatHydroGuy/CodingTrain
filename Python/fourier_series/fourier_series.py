import ctypes
import math
from collections import deque

import pygame
from pygame._sdl2 import Window


class FourierSeries:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)

        pygame.init()
        # pygame.mixer.init()
        pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)
        self.pg_window = Window.from_display_module()

        self.__scene_time = pygame.time.get_ticks()

        self.__sounds = ()

        self.time = 0

    def start(self) -> None:
        circle_x = self.screen_width / 3
        circle_y = self.screen_height / 2
        circle_color = (100, 100, 150)
        point_color = (50, 50, 100)
        line_color = (255, 255, 255)
        wave_color = (255, 0, 255)

        wave_q = deque([])

        while 1:
            self.__clock.tick(60)

            self.screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update()
            x = 0
            y = 0
            wave_offset = self.screen_width / 2.5
            num_epicycles = 5
            for i in range(num_epicycles):
                prev_x = x
                prev_y = y

                # circle_radius, x, y = self.saw_tooth_wave(i, x, y)
                circle_radius, x, y = self.square_wave(i, x, y)

                # render()
                pygame.draw.circle(self.screen, circle_color, (circle_x + prev_x, circle_y + prev_y),
                                   math.fabs(circle_radius), 1)
                pygame.draw.circle(self.screen, point_color, (circle_x + x, circle_y + y), 5)
                pygame.draw.line(self.screen, line_color, (circle_x + prev_x, circle_y + prev_y),
                                 (circle_x + x, circle_y + y), 1)

                prev_q_val = None
                for idx, q_val in enumerate(wave_q):
                    if idx == 0:
                        if i == num_epicycles - 1:
                            pygame.draw.line(self.screen, (128, 0, 255), (circle_x + x, circle_y + y),
                                             (circle_x + wave_offset, q_val + circle_y), 1)
                        pygame.draw.circle(self.screen, wave_color, (circle_x + wave_offset + idx, q_val + circle_y), 1)
                    else:
                        pygame.draw.line(self.screen, wave_color, (circle_x + wave_offset + idx, q_val + circle_y),
                                         (circle_x + wave_offset + idx, prev_q_val + circle_y), 1)
                    prev_q_val = q_val

            wave_q.appendleft(y)
            if len(wave_q) > 350:
                wave_q.pop()

            self.time += 0.01

            pygame.display.update()

    def square_wave(self, i, x, y):
        n = 2 * i + 1
        square_factor = 4.0 / (n * math.pi)
        circle_radius = self.screen_height / 5 * square_factor
        x += circle_radius * math.cos(n * self.time)
        y += circle_radius * math.sin(n * self.time)
        return circle_radius, x, y

    def saw_tooth_wave(self, i, x, y):
        m = i + 1
        triangle_factor = 2 * (-1) ** m / (m * math.pi)
        circle_radius = self.screen_height / 5 * triangle_factor
        x += circle_radius * math.cos(m * self.time)
        y += circle_radius * math.sin(m * self.time)
        return circle_radius, x, y
