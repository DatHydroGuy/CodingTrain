import math
from random import uniform
import pygame
from opensimplex import noise2
from pygame.locals import (K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_KP_MINUS, K_KP_PLUS, K_KP_DIVIDE,
                           K_KP_MULTIPLY, K_KP_PERIOD, K_KP_0)
from boundary import Boundary
from ray_source import RaySource

WINDOW_WIDTH = 1800
SCREEN_WIDTH = WINDOW_WIDTH / 2
SCREEN_HEIGHT = 900

ALPHA_PIVOT = 305  # 305 = 255 + 50, and these are the 2 alpha values we'll toggle between
curr_alpha = 255

render_fov = 60

noise_X = 0
noise_Y = 10000
noise_dir = 99999


def rescale_number_range(old_value, old_min, old_max, new_min, new_max):
    new_value = (((old_value - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min
    return min(new_min, max(new_max, int(new_value)))


def regenerate_boundaries():
    bounds = []
    for _ in range(5):
        bounds.append(Boundary(uniform(0, SCREEN_WIDTH), uniform(0, SCREEN_HEIGHT),
                               uniform(0, SCREEN_WIDTH), uniform(0, SCREEN_HEIGHT)))
    bounds.append(Boundary(0, 0, SCREEN_WIDTH - 1, 0))
    bounds.append(Boundary(SCREEN_WIDTH - 1, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1))
    bounds.append(Boundary(SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, 0, SCREEN_HEIGHT - 1))
    bounds.append(Boundary(0, SCREEN_HEIGHT - 1, 0, 0))
    return bounds


boundaries = regenerate_boundaries()

ray_source = RaySource(SCREEN_WIDTH, SCREEN_HEIGHT, render_fov)

mouse_x = 1
mouse_y = 1

use_euclidean_dist = False

control_scheme = 0  # 0 = Keyboard, 1 = Mouse, 2 = Perlin noise

pygame.init()
pygame.key.set_repeat(50, 10)

# create the drawing surface for the main window
window = pygame.display.set_mode((WINDOW_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)

# Create a surface with transparency support
ray_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
render_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

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
            elif event.key == K_KP_MINUS:
                render_fov -= 2
                if render_fov < 20:
                    render_fov = 20
                ray_source.change_fov(render_fov)
            elif event.key == K_KP_PLUS:
                render_fov += 2
                if render_fov > 120:
                    render_fov = 120
                ray_source.change_fov(render_fov)
            elif event.key == K_KP_DIVIDE:
                use_euclidean_dist = not use_euclidean_dist
            elif event.key == K_KP_MULTIPLY:
                curr_alpha = ALPHA_PIVOT - curr_alpha
            elif event.key == K_KP_0:
                control_scheme = (control_scheme + 1) % 3
            elif event.key == K_KP_PERIOD:
                boundaries = regenerate_boundaries()
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
        # did the user click the close window button? If so, then exit program
        elif event.type == QUIT:
            running = False

        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            ray_source.rotate(-1)
        if keys[K_RIGHT]:
            ray_source.rotate(1)
        if keys[K_UP]:
            ray_source.move(1)
        if keys[K_DOWN]:
            ray_source.move(-1)

    pressed_keys = pygame.key.get_pressed()

    # fill the background with black; use (0, 0, 0, 50) for cool visual echo effects
    ray_screen.fill((0, 0, 0, curr_alpha))
    render_screen.fill((0, 0, 0, curr_alpha))

    # update
    for boundary in boundaries:
        boundary.show(ray_screen)

    if control_scheme == 1:
        # Move ray_source with mouse cursor
        ray_source.update(mouse_x, mouse_y)
    elif control_scheme == 2:
        # Move ray_source with Perlin Noise
        update_x = (0.5 + 0.5 * noise2(noise_X, noise_Y)) * SCREEN_WIDTH
        update_y = (0.5 + 0.5 * noise2(noise_Y, noise_X)) * SCREEN_HEIGHT
        update_r = noise2(noise_X, noise_Y) * 3
        ray_source.update(update_x, update_y)
        ray_source.rotate(update_r)

    render_strips = ray_source.intersect(ray_screen, boundaries, use_euclidean_dist)
    ray_source.show(ray_screen)

    render_strip_width = SCREEN_WIDTH / len(render_strips)
    dist_proj_plane = SCREEN_WIDTH / 8 / math.tan(math.radians(render_fov // 2))
    max_sq = SCREEN_WIDTH * SCREEN_WIDTH
    for i in range(len(render_strips)):
        sq = render_strips[i] * render_strips[i]
        col_val = rescale_number_range(sq, 0, max_sq, 255, 0)
        col = pygame.Color(col_val, col_val, col_val)
        if use_euclidean_dist:
            strip_height = rescale_number_range(render_strips[i], 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0)
        else:
            strip_height = (SCREEN_HEIGHT / render_strips[i]) * dist_proj_plane if render_strips[i] != 0 else\
                SCREEN_HEIGHT
        strip_top = (SCREEN_HEIGHT - strip_height) / 2
        pygame.draw.rect(render_screen, col,
                         (i * render_strip_width, strip_top, render_strip_width + 1, strip_height))

    noise_X += 0.003
    noise_Y += 0.003
    noise_dir += 0.003

    # update the display
    window.blit(ray_screen, (0, 0))
    window.blit(render_screen, (SCREEN_WIDTH, 0))
    pygame.display.flip()

    pygame.display.set_caption(f"{clock.get_fps()}")

    clock.tick(60)

# exit pygame
pygame.quit()
