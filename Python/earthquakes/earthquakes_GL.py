from math import hypot, radians, pi, sin, cos
from pathlib import Path
import ctypes
import pygame
import numpy
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
# from ShaderLoader import compile_shader

user32 = ctypes.windll.user32
SCREEN_WIDTH = 1000  # user32.GetSystemMetrics(0)
SCREEN_HEIGHT = 1000  # user32.GetSystemMetrics(1)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


def read_texture(filename):
    texture_image = pygame.image.load(filename).convert()
    img_data = pygame.surfarray.array3d(texture_image)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, texture_image.size[0], texture_image.size[1],
                 0, GL_RGB, GL_UNSIGNED_BYTE, img_data.transpose(1, 0, 2))
    return texture_id


def main():
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), OPENGL | DOUBLEBUF)
    glClearColor(0.0, 0.0, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)

    gluPerspective(40, (SCREEN_WIDTH / SCREEN_HEIGHT), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -4)  # Move sphere back from camera so we can see it
    prev_x_pos = 0
    prev_y_pos = 0
    zoom_in_amount = 1.05
    zoom_out_amount = 0.95

    # allow press and hold of control buttons
    pygame.key.set_repeat(1, 10)

    # pre-rotate sphere to view lat, lon = 0, 0
    glRotatef(90, 1, 0, 0)
    glRotatef(180, 0, 0, 1)
    world_texture = read_texture(r'res\world.jpg')
    # glRotatef(90, -1, 0, 0)
    # glRotatef(180, 0, 0, -1)

    lon = 144.9631
    lat = -37.8136

    sphere_radius = 1
    theta = radians(lat) + pi / 2
    phi = pi - radians(lon)
    x = sphere_radius * sin(theta) * cos(phi + pi / 2)  # offset of pi/2 to account for texture mapping offset
    y = sphere_radius * sin(theta) * sin(phi + pi / 2)  # offset of pi/2 to account for texture mapping offset
    z = sphere_radius * cos(theta)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    glRotatef(1, 0, 1, 0)
                if event.key == pygame.K_RIGHT:
                    glRotatef(1, 0, -1, 0)
                if event.key == pygame.K_UP:
                    glRotatef(1, -1, 0, 0)
                if event.key == pygame.K_DOWN:
                    glRotatef(1, 1, 0, 0)
                if event.key == pygame.K_KP_PLUS:
                    glScaled(zoom_in_amount, zoom_in_amount, zoom_in_amount)
                if event.key == pygame.K_KP_MINUS:
                    glScaled(zoom_out_amount, zoom_out_amount, zoom_out_amount)

            # Zoom with mouse wheel
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # wheel up - zoom in
                    glScaled(zoom_in_amount, zoom_in_amount, zoom_in_amount)
                if event.button == 5:  # wheel down - zoom out
                    glScaled(zoom_out_amount, zoom_out_amount, zoom_out_amount)

            # Rotate with mouse drag
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                delta_x = mouse_x - prev_x_pos
                delta_y = mouse_y - prev_y_pos
                mouse_state = pygame.mouse.get_pressed()
                if mouse_state[0]:
                    model_view = (GLfloat * 16)()
                    glGetFloatv(GL_MODELVIEW_MATRIX, model_view)

                    # To combine x-axis and y-axis rotation
                    combined = (GLfloat * 3)()
                    combined[0] = model_view[0] * delta_y + model_view[1] * delta_x
                    combined[1] = model_view[4] * delta_y + model_view[5] * delta_x
                    combined[2] = model_view[8] * delta_y + model_view[9] * delta_x
                    norm_xy = hypot(combined[0], combined[1], combined[2])
                    glRotatef(hypot(delta_x, delta_y),
                              combined[0] / norm_xy, combined[1] / norm_xy, combined[2] / norm_xy)

                prev_x_pos = mouse_x
                prev_y_pos = mouse_y

        display()
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, world_texture)
        gluSphere(quadric, sphere_radius, 50, 50)
        gluDeleteQuadric(quadric)
        glDisable(GL_TEXTURE_2D)

        glTranslated(x, y, z)
        quadric = gluNewQuadric()
        gluCylinder(quadric, 0.01, 0.01, 0.1, 4, 4)
        gluDeleteQuadric(quadric)
        glTranslated(-x, -y, -z)

        pygame.display.set_caption("FPS: %.2f" % clock.get_fps())
        pygame.display.flip()
        clock.tick(100)


if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
