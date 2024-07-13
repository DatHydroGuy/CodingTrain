import ctypes
import pygame
from pygame import Vector2
from math import sin, cos, pi


class DoublePendulum:
    def __init__(self) -> None:
        user32 = ctypes.windll.user32
        self.screen_width = 1000  # user32.GetSystemMetrics(0)
        self.screen_height = 1000  # user32.GetSystemMetrics(1)

        pygame.init()
        pygame.display.set_caption("PyGame Framework")

        self.__clock = pygame.time.Clock()

        window_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF, 32)

    def start(self) -> None:
        length1 = 200
        length2 = 200
        mass1 = 20
        mass2 = 20
        angle1 = pi / 2
        angle2 = pi / 2
        angle1_vel = 0
        angle2_vel = 0
        g = 1
        origin = Vector2(self.screen_width / 2, self.screen_height / 2)
        tracing = []

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exit()

            # update
            self.screen.fill((0, 0, 0))

            x1 = length1 * sin(angle1)
            y1 = length1 * cos(angle1)
            pos1 = origin + Vector2(x1, y1)
            x2 = pos1.x + length2 * sin(angle2)
            y2 = pos1.y + length2 * cos(angle2)
            pos2 = Vector2(x2, y2)
            tracing.append(pos2)

            # render
            for idx, pt in enumerate(tracing[:-1]):
                pygame.draw.line(self.screen, (255, 255, 0), pt, tracing[idx + 1], 1)
            pygame.draw.line(self.screen, (255, 255, 255), origin, pos1, 1)
            pygame.draw.circle(self.screen, (255, 255, 255), pos1, mass1 // 2)
            pygame.draw.line(self.screen, (255, 255, 255), pos1, pos2, 1)
            pygame.draw.circle(self.screen, (255, 255, 255), pos2, mass2 // 2)

            num11 = -g * (2 * mass1 + mass2) * sin(angle1)
            num12 = -mass2 * g * sin(angle1 - 2 * angle2)
            num13 = -2 * sin(angle1 - angle2) * mass2
            num14 = angle2_vel * angle2_vel * length2 + angle1_vel * angle1_vel * length1 * cos(angle1 - angle2)
            numerator1 = num11 + num12 + num13 * num14
            den1 = length1 * (2 * mass1 + mass2 - mass2 * cos(2 * angle1 - 2 * angle2))
            angle1_acc = numerator1 / den1
            num21 = 2 * sin(angle1 - angle2)
            num22 = angle1_vel * angle1_vel * length1 * (mass1 + mass2)
            num23 = g * (mass1 + mass2) * cos(angle1)
            num24 = angle2_vel * angle2_vel * length2 * mass2 * cos(angle1 - angle2)
            numerator2 = num21 * (num22 + num23 + num24)
            den2 = length2 * (2 * mass1 + mass2 - mass2 * cos(2 * angle1 - 2 * angle2))
            angle2_acc = numerator2 / den2

            angle1_vel += angle1_acc
            angle2_vel += angle2_acc
            angle1 += angle1_vel
            angle2 += angle2_vel

            # optional dampening
            # angle1_vel *= 0.999
            # angle2_vel *= 0.999

            pygame.display.update()
            self.__clock.tick(60)
