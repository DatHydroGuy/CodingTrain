from random import uniform
import pygame
from opensimplex import noise2
from pygame.locals import (K_UP, K_DOWN, K_ESCAPE, KEYDOWN, QUIT)
from boundary import Boundary
from ray_source import RaySource

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000

noise_X = 0
noise_Y = 10000

boundaries = []
for _ in range(5):
    boundaries.append(Boundary(uniform(0, SCREEN_WIDTH), uniform(0, SCREEN_HEIGHT),
                               uniform(0, SCREEN_WIDTH), uniform(0, SCREEN_HEIGHT)))
boundaries.append(Boundary(0, 0, SCREEN_WIDTH, 0))
boundaries.append(Boundary(SCREEN_WIDTH, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
boundaries.append(Boundary(SCREEN_WIDTH, SCREEN_HEIGHT, 0, SCREEN_HEIGHT))
boundaries.append(Boundary(0, SCREEN_HEIGHT, 0, 0))

ray_source = RaySource(SCREEN_WIDTH, SCREEN_HEIGHT)

mouse_x = 0
mouse_y = 0

pygame.init()

# create the drawing surface for the main window
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)

# Create a surface with transparency support
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

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
            elif event.key == K_UP:
                pass
            elif event.key == K_DOWN:
                pass
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
        # did the user click the close window button? If so, then exit program
        elif event.type == QUIT:
            running = False

    pressed_keys = pygame.key.get_pressed()

    # fill the background with black (alpha value causes a neat ghosting effect)
    screen.fill((0, 0, 0, 50))
    # screen.fill((0, 0, 0))

    # update
    for boundary in boundaries:
        boundary.show(screen)

    # ray_source.update(mouse_x, mouse_y)
    update_x = (0.5 + 0.5 * noise2(noise_X, noise_Y)) * SCREEN_WIDTH
    update_y = (0.5 + 0.5 * noise2(noise_Y, noise_X)) * SCREEN_HEIGHT
    ray_source.update(update_x, update_y)
    ray_source.intersect(screen, boundaries)
    ray_source.show(screen)

    noise_X += 0.004
    noise_Y += 0.004

    # update the display
    window.blit(screen, (0, 0))
    pygame.display.flip()

    pygame.display.set_caption(f"{clock.get_fps()}")

    clock.tick(60)

# exit pygame
pygame.quit()
