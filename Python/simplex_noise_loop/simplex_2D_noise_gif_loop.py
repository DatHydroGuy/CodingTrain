import ctypes
from math import pi, sin, cos
import opensimplex
import pygame
from PIL import Image
from pygame import pixelcopy
from numpy import interp, uint8, moveaxis, array
from pygame._sdl2 import Window

# Render final GIF with the following at the command prompt:
# ffmpeg -f image2 -framerate 30 -i simplex_2D_loop-test%3d.png simplex_2D_loop_test_50.gif


class Simplex2dNoiseGifLoop:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 300  # user32.GetSystemMetrics(0)
        self.screen_height = 200  # user32.GetSystemMetrics(1)

        pygame.init()

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.window = pygame.display.set_mode(window_size)
        self.pg_window = Window.from_display_module()

    def start(self) -> None:
        running = True
        record = True
        frames = 100
        counter = 0
        opensimplex.random_seed()
        filename = f"simplex_2D_loop-test{frames}.gif"
        fps = 50
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
            self.window.fill((0, 0, 0))

            if record:
                percent = counter / frames
            else:
                percent = (counter % frames) / frames

            # render
            frame = array(self.render(percent), dtype=uint8).transpose((1, 0, 2))
            pixelcopy.array_to_surface(self.window, frame)  # fast copy colour array to screen

            if record:
                if counter == frames - 1:
                    running = False

            counter += 1

            pygame.display.set_caption(f"Rendered frame {counter} of {frames}")
            if record:
                curr_surface = pygame.display.get_surface()
                x3 = pygame.surfarray.array3d(curr_surface)
                x3 = moveaxis(x3, 0, 1)
                image_array = Image.fromarray(uint8(x3))
                # image_array.save(f"simplex_2D_loop-test{counter:03}.png")  # use this line for ffmpeg method
                frame_array.append(image_array)                            # use this line for PIL method
            pygame.display.flip()
            self.__clock.tick(50)
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

    def render(self, percent):
        angle = percent * 2 * pi
        noise_radius = 1.5
        noise = [[0 for x in range(self.screen_width)] for y in range(self.screen_height)]
        noise_max = 5
        if angle < pi * 2:
            noise_space_u = interp(noise_radius * cos(angle), [-1, 1], [3, noise_max])
            noise_space_v = interp(noise_radius * sin(angle), [-1, 1], [3, noise_max])

            x_off = 0
            for x in range(self.screen_width):
                x_off += 0.02
                y_off = 0
                for y in range(self.screen_height):
                    y_off += 0.02
                    temp = int(interp(opensimplex.noise4(x_off, y_off, noise_space_u, noise_space_v), [-1, 1], [0, 255]))
                    noise[y][x] = [temp, temp, temp]

            return noise
