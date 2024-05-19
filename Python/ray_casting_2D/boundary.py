import pygame


class Boundary:
    def __init__(self, x1, y1, x2, y2):
        self.a = pygame.Vector2(x1, y1)
        self.b = pygame.Vector2(x2, y2)

    def show(self, surface):
        pygame.draw.line(surface, pygame.Color(255, 100, 255), self.a, self.b, 1)
