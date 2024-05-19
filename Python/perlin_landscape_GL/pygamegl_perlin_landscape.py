import math
import time
from pathlib import Path

from OpenGL.GL import *
import ctypes
import pygame
import numpy as np
import pyrr
import opensimplex

from ShaderLoader import compile_shader


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCL = 20
COLS = SCREEN_WIDTH // SCL
ROWS = SCREEN_HEIGHT // SCL
X_MIN = -0.5
X_MAX = 0.5
X_STEP = (X_MAX - X_MIN) / COLS
Y_MIN = -0.5
Y_MAX = 0.5
Y_STEP = (Y_MAX - Y_MIN) / ROWS

vertices = []
indices = []

# noise = vnoise.Noise()
opensimplex.seed(time.time_ns())

for y in range(ROWS + 1):
    if 0 < y < ROWS:
        indices.append(y * (COLS + 1))
    for x in range(COLS + 1):
        vertices.extend([X_MIN + x * X_STEP, Y_MAX - y * Y_STEP, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        if y < ROWS:
            indices.extend([x + y * (COLS + 1), x + (y + 1) * (COLS + 1)])
    if y < ROWS - 1:
        last = indices[-1]
        extension = []
        for z in range(COLS + 1):
            extension.append(last - z)
            extension.append(last - z)
        indices.extend(extension)

vertices = np.array(vertices, dtype=np.float32)
vertices_row_length = 8

indices.append(indices[-1])
indices.append(indices[-1])
indices = np.array(indices, dtype=np.uint32)


def init_gl():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.1, 1.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glDepthFunc(GL_LEQUAL)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


def create_object(shader):
    # Create a new VAO (Vertex Array Object) and bind it
    vertex_array_object = glGenVertexArrays(1)
    glBindVertexArray(vertex_array_object)

    # Generate buffers to hold our vertices
    vertex_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)

    # Generate buffers to hold buffer indices
    element_buffer = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer)

    # Set the position of the 'position' in parameter of our shader and bind it.
    position = 0
    glBindAttribLocation(shader, position, 'position')
    glEnableVertexAttribArray(position)
    # Describe the position data layout in the buffer
    glVertexAttribPointer(position, 4, GL_FLOAT, False, vertices.itemsize * vertices_row_length, ctypes.c_void_p(0))

    # Set the position of the 'colour' in parameter of our shader and bind it.
    colour = 1
    glBindAttribLocation(shader, colour, 'colour')
    glEnableVertexAttribArray(colour)
    # Describe the position data layout in the buffer
    glVertexAttribPointer(colour, 4, GL_FLOAT, False, vertices.itemsize * vertices_row_length, ctypes.c_void_p(16))

    # Send the data over to the buffers
    glBufferData(GL_ARRAY_BUFFER, vertices.itemsize * len(vertices), vertices, GL_DYNAMIC_DRAW)       # Vertices array
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.itemsize * len(indices), indices, GL_STATIC_DRAW)  # Indices array

    # Unbind the VAO first (Important)
    glBindVertexArray(0)

    # Unbind other stuff
    glDisableVertexAttribArray(position)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    return vertex_array_object, vertex_buffer


def display(shader, vertex_array_object, aspect_ratio):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    rot_x = pyrr.matrix44.create_from_x_rotation(math.pi / 3, dtype=np.float32)
    transform_location = glGetUniformLocation(shader, 'transformation')
    glUniformMatrix4fv(transform_location, 1, GL_FALSE, rot_x)

    view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -0.7]))
    projection = pyrr.matrix44.create_perspective_projection_matrix(45.0, aspect_ratio, 0.1, 100.0)
    model = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0.0]))

    view_loc = glGetUniformLocation(shader, 'view')
    proj_loc = glGetUniformLocation(shader, 'projection')
    modl_loc = glGetUniformLocation(shader, 'model')

    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(modl_loc, 1, GL_FALSE, model)

    glBindVertexArray(vertex_array_object)
    glDrawElements(GL_TRIANGLE_STRIP, len(indices), GL_UNSIGNED_INT, None)
    glBindVertexArray(0)


def window_resize(width, height):
    pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
    glViewport(0, 0, width, height)


def main():
    window_width = SCREEN_WIDTH
    window_height = SCREEN_HEIGHT

    pygame.init()
    window_resize(window_width, window_height)
    init_gl()
    shader = compile_shader(Path('shaders', 'landscape.vert'),
                            Path('shaders', 'landscape.frag'))
    glUseProgram(shader)

    clock = pygame.time.Clock()
    vertex_array_object, vertex_buffer = create_object(shader)
    move_vel = 0
    looping = True

    while looping:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                looping = False
            elif event.type == pygame.VIDEORESIZE:
                window_width, window_height = event.size
                window_resize(window_width, window_height)
            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                looping = False

        # update
        y_off = move_vel
        for j in range(ROWS + 2):
            x_off = move_vel
            for i in range(COLS + 2):
                noise_val = opensimplex.noise2(x_off / (ROWS + 2), y_off / (COLS + 2))
                # noise_val = noise.noise2(x_off / (ROWS + 2), y_off / (COLS + 2))
                idx = (j * COLS + i) * vertices_row_length + 2
                if idx < len(vertices):
                    vertices[idx] = (noise_val - 0.5) / 15
                x_off += 10
            y_off += 10
        move_vel -= 0.6

        # Convert numpy array to ctypes pointer for glBufferSubData
        vertices_ptr = vertices.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        # Update the VBO with the new vertices data
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
        glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices_ptr)

        # Ensure the VAO is bound to the updated VBO
        glBindVertexArray(vertex_array_object)

        display(shader, vertex_array_object, window_width / window_height)
        pygame.display.set_caption("FPS: %.2f" % clock.get_fps())
        pygame.display.flip()
        clock.tick(100)

    glUseProgram(0)


if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
