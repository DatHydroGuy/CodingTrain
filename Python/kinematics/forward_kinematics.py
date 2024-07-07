import ctypes
import pygame
from pygame import Vector2
from forward_segment import Segment


class ForwardKinematics:
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
        segment_length = 50
        segment_width = 10
        phase = 0
        tentacle = Segment(Vector2(self.screen_width / 2, self.screen_height), segment_length, 0, phase, segment_width)

        curr_seg = tentacle
        for _ in range(20):
            phase += 0.1
            segment_length *= 0.9
            segment_width *= 0.9
            next_seg = Segment(Vector2(0, 0), segment_length, 0, phase, segment_width)
            curr_seg.add_child(next_seg)
            curr_seg = next_seg

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))

            next_seg = tentacle
            while next_seg is not None:
                next_seg.rotate()
                next_seg.update()

                # render
                next_seg.show(self.screen)
                next_seg = next_seg.child

            self.__clock.tick(60)
            pygame.display.update()
