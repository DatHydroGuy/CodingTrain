import ctypes
from math import pi

import pygame
from PIL import Image
from numpy import moveaxis, uint8
from pygame._sdl2 import Window
from particle import Particle


class SimplexNoiseGifLoop:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 1000  # user32.GetSystemMetrics(0)
        self.screen_height = 800  # user32.GetSystemMetrics(1)

        pygame.init()

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.window = pygame.display.set_mode(window_size)
        self.pg_window = Window.from_display_module()

    def start(self) -> None:
        running = True
        record = True
        frames = 240
        counter = 0
        particles = [Particle() for _ in range(100)]
        filename = "simplex_noise.gif"
        fps = 60
        frame_duration = int(1000 / fps)
        frame_array = []

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.window.fill((0, 0, 0, 0))

            if record:
                percent = counter / frames
            else:
                percent = (counter % frames) / frames

            # render
            self.render(percent, particles)

            if record:
                if counter == frames - 1:
                    running = False

            counter += 1

            pygame.display.set_caption(f"{self.__clock.get_fps()}")
            if record:
                curr_surface = pygame.display.get_surface()
                x3 = pygame.surfarray.array3d(curr_surface)
                x3 = moveaxis(x3, 0, 1)
                image_array = Image.fromarray(uint8(x3))
                # image_array.save(f"simplex_2D_loop-test{counter:03}.png")  # use this line for ffmpeg method
                frame_array.append(image_array)  # use this line for PIL method
            pygame.display.flip()
            self.__clock.tick(60)
        if record:
            if len(frame_array) > 0:
                frame_array[0].save(
                    filename,
                    save_all=True,
                    optimize=False,
                    append_images=frame_array[1:],
                    loop=0,
                    duration=frame_duration,
                )
        exit()

    def render(self, percent, particles):
        angle = percent * 2 * pi
        for particle in particles:
            s, x, y = particle.render(angle, self.screen_width, self.screen_height)
            self.window.blit(s, (x, y))
