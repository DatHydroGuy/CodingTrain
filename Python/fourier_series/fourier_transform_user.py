import ctypes
import math
from collections import deque

import pygame
from pygame._sdl2 import Window


class FourierTransformUser:
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

        self.time = 0

    def start(self) -> None:
        USER = 0
        FOURIER = 1
        state = -1
        wave_color = (255, 0, 255)

        path_queue = deque()
        drawing = []
        mouse_x = 0
        mouse_y = 0
        fourier_x = 0
        fourier_y = 0
        horiz_x = 0
        horiz_y = 0
        vert_x = 0
        vert_y = 0
        num_epicycles = 0
        prev_pt = (0, 0)

        while 1:
            self.__clock.tick(60)

            self.screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        state = USER
                        mouse_x, mouse_y = event.pos
                        path_queue = deque()
                        drawing = []
                        self.time = 0

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        state = FOURIER
                        x = [x[0] for x in drawing]
                        fourier_x = self.discrete_fourier_transform(x)
                        fourier_x.sort(key=lambda x: x['amp'], reverse=True)
                        horiz_x = 0
                        # ignore the epicycle at idx = 0 as it merely provides the offset from (x, y) = (0, 0)
                        horiz_y = int(sum(x['amp'] for x in fourier_x[1:3]))

                        y = [y[1] for y in drawing]
                        fourier_y = self.discrete_fourier_transform(y)
                        fourier_y.sort(key=lambda y: y['amp'], reverse=True)
                        # ignore the epicycle at idx = 0 as it merely provides the offset from (x, y) = (0, 0)
                        vert_x = int(sum(y['amp'] for y in fourier_y[1:3]))
                        vert_y = 0

                        num_epicycles = len(fourier_y)

                elif event.type == pygame.MOUSEMOTION:
                    if state == USER:
                        mouse_x, mouse_y = event.pos
                        for idx, pt in enumerate(drawing):
                            if idx == 0:
                                pygame.draw.circle(self.screen, wave_color, pt, 1)
                            else:
                                pygame.draw.line(self.screen, wave_color, pt, prev_pt, 1)
                            prev_pt = pt

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            if state == USER:
                drawing.append((mouse_x, mouse_y))
            elif state == FOURIER:
                # update
                xx, xy = self.create_epicycles(horiz_x, horiz_y, 0, fourier_x)
                yx, yy = self.create_epicycles(vert_x, vert_y, math.pi / 2, fourier_y)

                # render
                for i in range(num_epicycles):
                    prev_path_val = None
                    for idx, path_val in enumerate(path_queue):
                        if idx == 0:
                            pygame.draw.line(self.screen, (128, 0, 255), (xx, xy), path_val, 1)
                            pygame.draw.line(self.screen, (128, 0, 255), (yx, yy), path_val, 1)
                            pygame.draw.circle(self.screen, wave_color, path_val, 1)
                        else:
                            pygame.draw.line(self.screen, wave_color, path_val, prev_path_val, 1)
                        prev_path_val = path_val

                path_queue.appendleft((xx, yy))
                if len(path_queue) > len(drawing):
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
                pygame.draw.circle(self.screen, circle_color, (prev_x, prev_y),
                                   math.fabs(circle_radius), 1)
                pygame.draw.circle(self.screen, point_color, (x, y), 5)
                pygame.draw.line(self.screen, line_color, (prev_x, prev_y),
                                 (x, y), 1)
        return x, y

    @staticmethod
    def discrete_fourier_transform(x):
        transform = []
        num_elements = len(x)
        const_val = 2 * math.pi / num_elements
        for k in range(num_elements):
            re = 0
            im = 0
            for n in range(num_elements):
                phi = const_val * k * n
                re += x[n] * math.cos(phi)
                im -= x[n] * math.sin(phi)

            re /= num_elements
            im /= num_elements

            freq = k
            amp = math.sqrt(re * re + im * im)
            phase = math.atan2(im, re)

            transform.append({'re': re, 'im': im, 'freq': freq, 'amp': amp, 'phase': phase})
        return transform
