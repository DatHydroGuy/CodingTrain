import ctypes
import pygame
from pygame import Vector2
from random import uniform
from tentacle import Tentacle


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
        num_segments = 20
        tentacles = [Tentacle(Vector2(0, self.screen_height / 2), num_segments, segment_length),
                     Tentacle(Vector2(self.screen_width, self.screen_height / 2), num_segments, segment_length)]
        ball_pos = Vector2(uniform(0, self.screen_width), uniform(0, self.screen_height))
        ball_vel = Vector2(uniform(-8, 8), uniform(-6, 6))
        ball_acc = Vector2(0, 0)
        ball_radius = 20

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

            for tentacle in tentacles:
                # tentacle.update(mouse_x, mouse_y)
                tentacle.update(ball_pos.x, ball_pos.y)

            # render
            for tentacle in tentacles:
                tentacle.show(self.screen)

            pygame.draw.circle(self.screen, (100, 255, 0), ball_pos, ball_radius)

            ball_vel += ball_acc
            ball_pos += ball_vel
            if ball_pos.x < ball_radius or ball_pos.x > self.screen_width - ball_radius:
                ball_vel.x *= -1
            if ball_pos.y < ball_radius or ball_pos.y > self.screen_height - ball_radius:
                ball_vel.y *= -1

            self.__clock.tick(60)
            pygame.display.update()
