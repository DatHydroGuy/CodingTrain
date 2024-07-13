import ctypes
import pygame
from numpy import round, ndarray, array, float64


class FloydSteinbergDithering:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 1024  # user32.GetSystemMetrics(0)
        self.screen_height = 512  # user32.GetSystemMetrics(1)

        pygame.init()
        pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)

    def start(self) -> None:
        kitten_image = pygame.image.load('res\\kitten.jpg').convert()
        kitten = pygame.surfarray.array3d(kitten_image).astype(float64)
        dithered = ndarray(kitten.shape)
        num_colour_steps = 2
        num_colour_steps -= 1

        kitten_width = kitten.shape[0]
        kitten_height = kitten.shape[1]

        for y in range(0, kitten_width):
            for x in range(0, kitten_height):
                orig_colour = array(kitten[x, y], dtype=float64)
                quantised_colour = round(num_colour_steps * orig_colour / 255) * int(255 / num_colour_steps)
                dithered[x, y] = quantised_colour
                colour_error = orig_colour - quantised_colour
                if x < kitten_width - 1:
                    kitten[x + 1, y] += 7 * colour_error / 16
                if y < kitten_height - 1:
                    if x > 1:
                        kitten[x - 1, y + 1] += 3 * colour_error / 16
                    kitten[x, y + 1] += 5 * colour_error / 16
                    if x < kitten_width - 1:
                        kitten[x + 1, y + 1] += colour_error / 16

        dithered_surf = pygame.surfarray.make_surface(dithered)

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))

            # render
            self.screen.blit(kitten_image, (0, 0))
            self.screen.blit(dithered_surf, (self.screen_width / 2, 0))

            pygame.display.update()
            self.__clock.tick(60)
