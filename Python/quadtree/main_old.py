from pygame.locals import (K_ESCAPE, KEYDOWN, QUIT, MOUSEBUTTONDOWN, MOUSEMOTION)
from random import random

from quadtree import *

# define constants for screen width and height
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 1024

pygame.init()

boundary = Rectangle(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
quad_tree = QuadTree(boundary, 1)

for i in range(500):
    p = Point(random() * SCREEN_WIDTH, random() * SCREEN_HEIGHT, None)
    quad_tree.insert(p)

rnd_rect = Rectangle(random() * SCREEN_WIDTH, random() * SCREEN_HEIGHT, 100, 100)

# create the drawing surface (screen)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()

# main loop
running = True
while running:

    # process user inputs
    for event in pygame.event.get():
        # did the user press a key?
        if event.type == KEYDOWN:
            # was it the escape key? If so, then exit program
            if event.key == K_ESCAPE:
                running = False
        # did the user click the close window button? If so, then exit program
        elif event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            quad_tree.insert(Point(event.pos[0], event.pos[1], None))
        elif event.type == MOUSEMOTION:
            rnd_rect = Rectangle(event.pos[0], event.pos[1], 100, 100)

    pressed_keys = pygame.key.get_pressed()

    # fill the background with black
    screen.fill((0, 0, 0))

    # update
    quad_tree.show(screen)

    pygame.draw.rect(screen, pygame.color.Color('green'),
                     (rnd_rect.x - rnd_rect.half_width, rnd_rect.y - rnd_rect.half_height,
                      rnd_rect.half_width * 2, rnd_rect.half_height * 2),
                     width=1)

    rnd_rect_pts = quad_tree.query(rnd_rect, [])
    for pt in rnd_rect_pts:
        pygame.draw.circle(screen, pygame.color.Color('red'), (pt.x, pt.y), 2)

    # update the display
    pygame.display.flip()

    clock.tick(60)

# exit pygame
pygame.quit()
