import ctypes
import pygame
from pygame import Vector2
from inverse_segment_fixed_point import Segment


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
        segment_length = 20
        segment_width = 4
        num_segments = 30
        tentacle = [Segment(Vector2(self.screen_width / 2, self.screen_height / 2), segment_length, segment_width)]
        for i in range(1, num_segments):
            tentacle.append(Segment(tentacle[i - 1].end, segment_length, segment_width))
        base_pos = Vector2(self.screen_width / 2, self.screen_height)

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

            end_seg = tentacle[num_segments - 1]
            end_seg.follow(mouse_x, mouse_y)
            end_seg.update()

            for i in range(num_segments - 2, -1, -1):
                tentacle[i].follow(tentacle[i + 1].position.x, tentacle[i + 1].position.y)
                tentacle[i].update()

            tentacle[0].constrain_position(base_pos)
            for i in range(1, num_segments):
                tentacle[i].constrain_position(tentacle[i - 1].end)

            # render
            for segment in tentacle:
                segment.show(self.screen)

            self.__clock.tick(60)
            pygame.display.update()
