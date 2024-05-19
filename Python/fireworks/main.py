from random import random
import pygame
from pygame.locals import (K_UP, K_DOWN, K_ESCAPE, KEYDOWN, QUIT)
from config import *
from firework import Firework

fireworks = []

pygame.init()

# create the drawing surface for the main window
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

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
        # did the user click the close window button? If so, then exit program
        elif event.type == QUIT:
            running = False

    pressed_keys = pygame.key.get_pressed()

    # fill the background with black
    screen.fill((0, 0, 0, 25))

    if random() < FIREWORK_LAUNCH_THRESHOLD:
        fireworks.append(Firework(SCREEN_WIDTH, SCREEN_HEIGHT))

    # update
    for firework in fireworks[::-1]:
        firework.update(GRAVITY)
        firework.draw(screen)
        if firework.done():
            fireworks.remove(firework)

    # update the display
    window.blit(screen, (0, 0))
    pygame.display.flip()

    # pygame.display.set_caption(f"{clock.get_fps()}")

    clock.tick(60)

# exit pygame
pygame.quit()
