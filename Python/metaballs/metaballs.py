import ctypes
from colorsys import hls_to_rgb
import numpy as np
import pygame
from pygame import Color, surfarray
from pygame._sdl2 import Window
from blob import Blob


class Metaballs:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 800  # user32.GetSystemMetrics(0)
        self.screen_height = 600  # user32.GetSystemMetrics(1)

        surfarray.use_arraytype('numpy')

        pygame.init()
        pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)
        self.pg_window = Window.from_display_module()

    @staticmethod
    def colour_by_hue(hue, lightness=0.5, saturation=1.0):
        r, g, b = hls_to_rgb(hue, lightness, saturation)
        r, g, b = [int(255 * i) for i in (r, g, b)]
        return Color(r, g, b, 255)

    def start(self) -> None:
        self.screen.fill((0, 0, 0))
        mid_x = self.screen_width / 2.0
        mid_y = self.screen_height / 2.0
        pix_arr = np.zeros((self.screen_width, self.screen_height, 3), dtype=np.uint32)
        Y, X = np.ogrid[:self.screen_height, :self.screen_width]

        b = Blob(200, 200, 4000, 0, 0)

        while 1:
            self.__clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            b.pos += pygame.Vector2(1, 0)
            dist = np.sqrt((X - b.pos.x) ** 2 + (Y - b.pos.y) ** 2)

            for y in range(self.screen_height):
                for x in range(self.screen_width):
                    if dist[y, x] == 0:
                        col = 255
                    else:
                        col = min(255, b.r / dist[y, x])
                    pix_arr[x, y] = (col, col, col)

            # render
            surfarray.blit_array(self.screen, pix_arr)

            pygame.display.set_caption(f'{self.__clock.get_fps()}')

            pygame.display.flip()
