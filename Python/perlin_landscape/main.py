import math

import opensimplex
from pygame.locals import (K_ESCAPE, KEYDOWN, QUIT)
from matrix import *


def connect(surface, a: pygame.Vector2, b: pygame.Vector2):
    pygame.draw.line(surface, (255, 255, 255), a, b, 1)


# Global declarations
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCL = 20
COLS = int(1.6 * SCREEN_WIDTH // SCL)
ROWS = int(1.1 * SCREEN_HEIGHT // SCL)
WIDTH_STEP = SCL / SCREEN_WIDTH
HEIGHT_STEP = SCL / SCREEN_HEIGHT
angle = math.pi / 3
c = math.cos(angle)
s = math.sin(angle)
rotate_x = [[1, 0, 0],
            [0, c, -s],
            [0, s, c]]
distance = 1.1
minima = -0.5
translate = pygame.Vector3(SCREEN_WIDTH / 3.2, SCREEN_HEIGHT / 2, 0)
z_vals = [[0 for _ in range(COLS + 2)] for _ in range(ROWS + 2)]
y_move = 0

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
        # did the user click the close window button? If so, then exit program
        elif event.type == QUIT:
            running = False

    pressed_keys = pygame.key.get_pressed()

    # fill the background with black
    screen.fill((0, 0, 0, 255))

    # update
    y_off = y_move
    for j in range(ROWS + 2):
        x_off = 0
        for i in range(COLS + 2):
            noise_val = opensimplex.noise2(x_off / (ROWS + 2), y_off / (COLS + 2))
            z_vals[j][i] = (noise_val - 0.5) / 15
            x_off += 10
        y_off += 10
    y_move -= 1

    # draw
    for y in range(ROWS + 1):
        step_y = y * HEIGHT_STEP
        step_y1 = step_y + HEIGHT_STEP

        for x in range(COLS + 1):
            step_x = x * WIDTH_STEP
            step_x1 = step_x + WIDTH_STEP

            ul = pygame.Vector3(minima + step_x, minima + step_y, z_vals[y][x])
            ur = pygame.Vector3(minima + step_x1, minima + step_y, z_vals[y][x + 1])
            ll = pygame.Vector3(minima + step_x, minima + step_y1, z_vals[y + 1][x])

            rotated_ul = matrix_mult_vec(rotate_x, ul)
            rotated_ur = matrix_mult_vec(rotate_x, ur)
            rotated_ll = matrix_mult_vec(rotate_x, ll)

            z = 1 / (distance - rotated_ul.z)
            proj_matrix = [[z, 0, 0],
                           [0, z, 0],
                           [0, 0, z]]
            proj_ul = matrix_mult_vec(proj_matrix, rotated_ul)

            z = 1 / (distance - rotated_ur.z)
            proj_matrix = [[z, 0, 0],
                           [0, z, 0],
                           [0, 0, z]]
            proj_ur = matrix_mult_vec(proj_matrix, rotated_ur)

            z = 1 / (distance - rotated_ll.z)
            proj_matrix = [[z, 0, 0],
                           [0, z, 0],
                           [0, 0, z]]
            proj_ll = matrix_mult_vec(proj_matrix, rotated_ll)

            ul = proj_ul * SCREEN_WIDTH + translate
            ur = proj_ur * SCREEN_WIDTH + translate
            ll = proj_ll * SCREEN_WIDTH + translate

            if y < ROWS:
                pygame.draw.line(screen, (255, 255, 255), ul.xy, ll.xy, 1)
            if x < COLS:
                pygame.draw.line(screen, (255, 255, 255), ul.xy, ur.xy, 1)
                if y < ROWS:
                    pygame.draw.line(screen, (255, 255, 255), ll.xy, ur.xy, 1)

    # update the display
    window.blit(screen, (0, 0))
    pygame.display.flip()

    pygame.display.set_caption(f"{clock.get_fps()}")

    clock.tick(60)

# exit pygame
pygame.quit()
