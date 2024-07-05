import pygame


class Circle:
    def __init__(self, pos, colour=(255, 255, 255, 255), radius=1, filled=False):
        self.pos = pos
        self.colour = colour
        self.radius = radius
        self.growing = True
        self.filled = filled

    def grow(self):
        if self.growing:
            self.radius += 1

    def edges(self, screen_width, screen_height):
        return (self.pos.x - self.radius <= 1 or self.pos.x + self.radius > screen_width or
                self.pos.y - self.radius <= 1 or self.pos.y + self.radius > screen_height)

    def draw(self, surface):
        pygame.draw.circle(surface, self.colour, self.pos, self.radius, 0 if self.filled else 1)
