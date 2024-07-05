import ctypes
from math import hypot, fabs
from random import randint
import pygame
from pygame import Vector2
from circle import Circle


class AnimatedCirclePacking:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 800  # user32.GetSystemMetrics(0)
        self.screen_height = 600  # user32.GetSystemMetrics(1)

        pygame.init()
        pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)
        image_file = pygame.image.load("res\\2024.png")
        pixels = pygame.surfarray.pixels2d(image_file)
        self.pixels = []
        for i in range(pixels.shape[0]):
            for j in range(pixels.shape[1]):
                if pixels[i, j] > 0:
                    self.pixels.append([i, j])

    def start(self) -> None:
        circles = []
        max_circles_per_frame = 10

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))
            curr_circle_count = 0
            attempts = 0
            while curr_circle_count < max_circles_per_frame:
                c = self.new_circle(circles)
                if c is not None:
                    circles.append(c)
                    curr_circle_count += 1
                attempts += 1
                if attempts > 1000:
                    break

            # render
            for circle in circles:
                if circle.growing:
                    if circle.edges(self.screen_width, self.screen_height):
                        circle.growing = False
                    else:
                        for other in circles:
                            if other is not circle:
                                dist = hypot(fabs(circle.pos.x - other.pos.x), fabs(circle.pos.y - other.pos.y))
                                if dist - 1 < circle.radius + other.radius:
                                    circle.growing = False
                                    break

                circle.draw(self.screen)
                circle.grow()

            self.__clock.tick(60)
            pygame.display.flip()

    def new_circle(self, circles):
        rand_pix_in_image = randint(0, len(self.pixels))
        x = self.pixels[rand_pix_in_image][0]
        y = self.pixels[rand_pix_in_image][1]

        valid = True
        for circle in circles:
            dist = hypot(fabs(x - circle.pos.x), fabs(y - circle.pos.y))
            if dist < circle.radius:
                valid = False
                break

        if valid:
            return Circle(Vector2(x, y), radius=1)
        else:
            return None
