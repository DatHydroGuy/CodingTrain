import csv
from math import hypot, radians, pi, sin, cos, sqrt
import pygame
from numpy import interp
from pygame import Vector3
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800


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
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_data.shape[0], img_data.shape[1],
                 0, GL_RGB, GL_UNSIGNED_BYTE, img_data.transpose(1, 0, 2))
    return texture_id


def read_earthquake_data(sphere_radius):
    quakes = []
    with open(r"res\all_month.csv", encoding='utf8', newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"', dialect='unix')
        for idx, row in enumerate(csv_reader):
            if idx == 0:
                continue
            lat = float(row[1])
            lon = float(row[2])
            mag = float(row[4])
            mag = sqrt(pow(10, mag))
            max_mag = sqrt(pow(10, 10))
            height = interp(mag, [0, max_mag], [0, 10])

            theta = radians(lat) + pi / 2
            phi = pi - radians(lon)
            x = sphere_radius * sin(theta) * cos(phi + pi / 2)  # offset of pi/2 to account for texture mapping offset
            y = sphere_radius * sin(theta) * sin(phi + pi / 2)  # offset of pi/2 to account for texture mapping offset
            z = sphere_radius * cos(theta)

            position = Vector3(x, y, z)
            z_axis = Vector3(0, 0, 1)   # gluCylinder is aligned to z-axis by default, so we rotate from it
            angle_between = z_axis.angle_to(position)
            rotation_axis = z_axis.cross(position)

            quakes.append((x, y, z, height, angle_between, rotation_axis))
    return quakes


def main():
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), OPENGL | DOUBLEBUF)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    gluPerspective(40, (SCREEN_WIDTH / SCREEN_HEIGHT), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -4)  # Move sphere back from camera so we can see it
    prev_x_pos = 0
    prev_y_pos = 0
    zoom_in_amount = 1.05
    zoom_out_amount = 0.95
    rotate_amount = 0.5

    # allow press and hold of control buttons
    pygame.key.set_repeat(1, 10)

    # pre-rotate sphere so that we are initially viewing lat, lon = 0, 0
    glRotatef(90, 1, 0, 0)
    glRotatef(180, 0, 0, 1)
    read_texture(r'res\world.jpg')

    sphere_radius = 1

    earthquake_data = read_earthquake_data(sphere_radius)
    glColor3f(1.0, 0.0, 1.0)  # Draw columns in magenta
    pygame.display.set_caption("Earthquake data for the last 30 days")

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
                    glRotatef(rotate_amount, 0, 0, 1)
                if event.key == pygame.K_RIGHT:
                    glRotatef(rotate_amount, 0, 0, -1)
                if event.key == pygame.K_UP:
                    glRotatef(rotate_amount, -1, 0, 0)
                if event.key == pygame.K_DOWN:
                    glRotatef(rotate_amount, 1, 0, 0)
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

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        gluSphere(quadric, sphere_radius, 50, 50)
        gluDeleteQuadric(quadric)
        glDisable(GL_TEXTURE_2D)

        for x, y, z, height, angle_between, rotation_axis in earthquake_data:
            glPushMatrix()
            glTranslated(x, y, z)
            glRotatef(angle_between, rotation_axis.x, rotation_axis.y, rotation_axis.z)
            quadric = gluNewQuadric()
            gluCylinder(quadric, 0.01, 0.01, height, 4, 1)
            gluDeleteQuadric(quadric)
            # Add end cap to cylinders (they are hollow by default)
            glTranslated(0, 0, height)
            quadric = gluNewQuadric()
            gluDisk(quadric, 0.0, 0.01, 4, 1)
            gluDeleteQuadric(quadric)
            glPopMatrix()

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
