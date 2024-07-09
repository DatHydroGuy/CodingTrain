import ctypes
import pygame
from pygame import Vector2
from inverse_segment import Segment
from numpy import interp


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
        mouse_x = None
        mouse_y = None
        segment_length = 15
        max_segment_width = 10
        num_segments = 40
        tentacle = Segment(Vector2(self.screen_width / 2, self.screen_height / 2), segment_length, 1)
        curr_seg = tentacle
        for i in range(num_segments - 1):
            width = interp(i + 1, [0, num_segments - 1], [1, max_segment_width])
            next_seg = Segment(curr_seg.end, segment_length, width)
            curr_seg.add_child(next_seg)
            curr_seg = next_seg

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.MOUSEMOTION:
                    mouse_x, mouse_y = event.pos

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update & render
            self.screen.fill((0, 0, 0))

            curr_seg.follow(mouse_x, mouse_y)
            curr_seg.update()
            curr_seg.show(self.screen)

            next_seg = curr_seg.parent
            while next_seg is not None:
                next_seg.follow(next_seg.child.position.x, next_seg.child.position.y)
                next_seg.update()
                next_seg.show(self.screen)
                next_seg = next_seg.parent

            self.__clock.tick(60)
            pygame.display.update()
