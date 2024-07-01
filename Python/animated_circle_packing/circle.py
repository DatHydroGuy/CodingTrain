import pygame


class Circle:
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius
        self.growing = True

    def grow(self):
        if self.growing:
            self.radius += 1

    def edges(self, screen_width, screen_height):
        return (self.pos.x - self.radius <= 0 or self.pos.x + self.radius > screen_width or
                self.pos.y - self.radius <= 0 or self.pos.y + self.radius > screen_height)

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255, 255), self.pos, self.radius, 1)
