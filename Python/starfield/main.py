import pygame
from pygame.locals import (K_UP, K_DOWN, K_ESCAPE, KEYDOWN, QUIT)
from random import random


# define constants for screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
NUM_STARS = 800
MAX_SPEED = 20


class Star:
    x = 0
    y = 0
    z = 0

    def __init__(self):
        self.x = random() * 2 * SCREEN_WIDTH - SCREEN_WIDTH
        self.y = random() * 2 * SCREEN_HEIGHT - SCREEN_HEIGHT
        self.z = random() * SCREEN_WIDTH

    def update(self, speed):
        self.z -= speed
        if self.z < 1:
            self.x = random() * 2 * SCREEN_WIDTH - SCREEN_WIDTH
            self.y = random() * 2 * SCREEN_HEIGHT - SCREEN_HEIGHT
            self.z = SCREEN_WIDTH

    def draw(self, scr):
        sx = SCREEN_WIDTH / 2 + SCREEN_WIDTH * self.x / self.z
        sy = SCREEN_HEIGHT / 2 + SCREEN_HEIGHT * self.y / self.z
        r = 10 - (self.z * 10 / SCREEN_WIDTH)
        pygame.draw.circle(scr, (255, 255, 255), (sx, sy), r)


pygame.init()

# create the drawing surface (screen)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

stars = [Star() for i in range(NUM_STARS)]

clock = pygame.time.Clock()

# main loop
star_speed = MAX_SPEED / 2
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
                star_speed += 1
                if star_speed > MAX_SPEED:
                    star_speed = MAX_SPEED
            elif event.key == K_DOWN:
                star_speed -= 1
                if star_speed < 1:
                    star_speed = 1
        # did the user click the close window button? If so, then exit program
        elif event.type == QUIT:
            running = False

    pressed_keys = pygame.key.get_pressed()

    # fill the background with black
    screen.fill((0, 0, 0))

    # update
    for star in stars:
        star.update(speed=star_speed)
        star.draw(screen)

    # update the display
    pygame.display.flip()

    clock.tick(60)

# exit pygame
pygame.quit()
