import ctypes
import math
from collections import deque
from dolphin200 import data

import pygame
from pygame._sdl2 import Window


class FourierTransformPatternComplex:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)

        pygame.init()
        pygame.display.set_caption("PyGame Framework")

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)
        self.pg_window = Window.from_display_module()

        self.__clock = pygame.time.Clock()
        self.__scene_time = pygame.time.get_ticks()

        self.queue_capacity = 200
        self.time = 0

    def start(self) -> None:
        wave_color = (255, 0, 255)
        x = [complex(x[0], x[1]) for x in data]
        fourier_x = self.discrete_fourier_transform(x)
        fourier_x.sort(key=lambda x: x['amp'], reverse=True)
        horiz_x = self.screen_width - sum(x['amp'] for x in fourier_x) - 25     # ensure all x values fit horizontally
        # ignore the epicycle at idx = 0 as it merely provides the offset from (x, y) = (0, 0)
        horiz_y = int(sum(x['amp'] for x in fourier_x[1:3]))

        num_epicycles = len(data)
        path_queue = deque()

        while 1:
            self.__clock.tick(60)

            self.screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            xx, xy = self.create_epicycles(horiz_x, horiz_y, 0, fourier_x)

            # render
            for i in range(num_epicycles):
                prev_path_val = None
                for idx, path_val in enumerate(path_queue):
                    if idx == 0:
                        pygame.draw.circle(self.screen, wave_color, (path_val.real, path_val.imag), 1)
                    else:
                        pygame.draw.line(self.screen, wave_color, (path_val.real, path_val.imag),
                                         (prev_path_val.real, prev_path_val.imag), 1)
                    prev_path_val = path_val

            path_queue.appendleft(complex(xx, xy))
            if len(path_queue) > self.queue_capacity:
                path_queue.pop()

            # one full rotation (2*PI radians) should take the entire fourier_y array to complete
            dt = 2 * math.pi / num_epicycles
            self.time += dt

            if self.time > 2 * math.pi:
                self.time = 0
                path_queue = deque()

            pygame.display.update()

    def create_epicycles(self, x, y, rotation, fourier):
        circle_color = (100, 100, 150)
        point_color = (50, 50, 100)
        line_color = (255, 255, 255)
        num_epicycles = len(fourier)

        for i in range(num_epicycles):
            prev_x = x
            prev_y = y

            freq = fourier[i]['freq']
            circle_radius = fourier[i]['amp']
            phase = fourier[i]['phase']
            x += circle_radius * math.cos(freq * self.time + phase + rotation)
            y += circle_radius * math.sin(freq * self.time + phase + rotation)

            # render
            # ignore the epicycle at idx = 0 as it merely provides the offset from (x, y) = (0, 0)
            if i >= 1:
                pygame.draw.circle(self.screen, circle_color, (prev_x, prev_y), math.fabs(circle_radius), 1)
                pygame.draw.circle(self.screen, point_color, (x, y), 5)
                pygame.draw.line(self.screen, line_color, (prev_x, prev_y), (x, y), 1)
        return x, y

    @staticmethod
    def discrete_fourier_transform(x):
        transform = []
        num_elements = len(x)
        const_val = 2 * math.pi / num_elements
        for k in range(num_elements):
            total = complex(0, 0)
            for n in range(num_elements):
                phi = const_val * k * n
                delta = complex(math.cos(phi), -math.sin(phi))
                total += x[n] * delta
            total = complex(total.real / num_elements, total.imag / num_elements)

            freq = k
            amp = math.sqrt(total.real * total.real + total.imag * total.imag)
            phase = math.atan2(total.imag, total.real)

            transform.append({'re': total.real, 'im': total.imag, 'freq': freq, 'amp': amp, 'phase': phase})
        return transform
