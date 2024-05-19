import random

from OpenGL.GL import *
import OpenGL.GL.shaders
import ctypes
import pygame
import numpy

from blob import Blob

# taken from https://jamie-wong.com/2016/07/06/metaballs-and-webgl/

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1000
NUM_METABALLS = 20

vertex_shader = """
#version 130
in vec2 position;

void main()
{
   gl_Position = vec4(position, 0.0, 1.0);
}
"""

fragment_shader = """
#version 130
precision highp float;
uniform vec3 metaballs[""" + f'{NUM_METABALLS}' + """];
const float WIDTH = """ + f'{SCREEN_WIDTH}' + """.0;
const float HEIGHT = """ + f'{SCREEN_HEIGHT}' + """.0;

void main()
{
    float x = gl_FragCoord.x;
    float y = gl_FragCoord.y;
    float v = 0.0;
    for (int i = 0; i < """ + f'{NUM_METABALLS}' + """; i++) {
        vec3 mb = metaballs[i];
        float dx = mb.x - x;
        float dy = mb.y - y;
        float r = mb.z;
        v += r * r / (dx * dx + dy * dy);
        if (v > 1.0) {
            gl_FragColor = vec4(x/WIDTH, y/HEIGHT, 0.0, 1.0);
        } else {
            gl_FragColor = vec4(0.0, 0.0, 0.1, 1.0);
        }
    }
}
"""

vertices = [-1.0, 1.0,
            -1.0, -1.0,
            1.0, -1.0,
            1.0, 1.0]
vertices = numpy.array(vertices, dtype=numpy.float32)

indices = [0, 1, 2,
           0, 2, 3]
indices = numpy.array(indices, dtype=numpy.uint32)


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

    # Get the position of the 'position' in parameter of our shader and bind it.
    position = glGetAttribLocation(shader, 'position')
    glEnableVertexAttribArray(position)

    # Describe the position data layout in the buffer
    glVertexAttribPointer(position, 2, GL_FLOAT, False, 8, ctypes.c_void_p(0))

    # # Get the position of the 'colour' in parameter of our shader and bind it.
    # colour = glGetAttribLocation(shader, 'colour')
    # glEnableVertexAttribArray(colour)
    #
    # # Describe the position data layout in the buffer
    # glVertexAttribPointer(colour, 4, GL_FLOAT, False, 32, ctypes.c_void_p(16))

    # Send the data over to the buffers
    glBufferData(GL_ARRAY_BUFFER, 32, vertices, GL_STATIC_DRAW)  # Vertices array
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, 24, indices, GL_STATIC_DRAW)  # Indices array

    # Unbind the VAO first (Important)
    glBindVertexArray(0)

    # Unbind other stuff
    glDisableVertexAttribArray(position)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    return vertex_array_object


def display(shader, vertex_array_object, data_for_gpu):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glUseProgram(shader)

    metaballs_loc = glGetUniformLocation(shader, "metaballs")
    glUniform3fv(metaballs_loc, NUM_METABALLS, data_for_gpu)

    glBindVertexArray(vertex_array_object)
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)  # Replaces glDrawArrays because we're drawing indices now.
    glBindVertexArray(0)

    glUseProgram(0)


def main():
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    glClearColor(0.0, 0.0, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)

    shader = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    )

    vertex_array_object = create_object(shader)

    min_dim = min(SCREEN_WIDTH, SCREEN_HEIGHT)
    blobs = []
    for i in range(NUM_METABALLS):
        radius = random.uniform(min_dim / (2 * NUM_METABALLS), min_dim / (NUM_METABALLS / 2))
        x = random.uniform(radius, SCREEN_WIDTH - radius)
        y = random.uniform(radius, SCREEN_HEIGHT - radius)
        vx = random.uniform(-5.0, 5.0)
        vy = random.uniform(-5.0, 5.0)
        blobs.append(Blob(x, y, radius, vx, vy))

    clock = pygame.time.Clock()

    while True:
        clock.tick(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                return

        metaballs = []
        for blob in blobs:
            blob.pos += blob.vel
            if blob.pos.x < blob.r:
                blob.pos.x = blob.r + 1
                blob.vel.x = -blob.vel.x
            if blob.pos.x + blob.r > SCREEN_WIDTH:
                blob.pos.x = SCREEN_WIDTH - blob.r
                blob.vel.x = -blob.vel.x
            if blob.pos.y < blob.r:
                blob.pos.y = blob.r + 1
                blob.vel.y = -blob.vel.y
            if blob.pos.y + blob.r > SCREEN_HEIGHT:
                blob.pos.y = SCREEN_HEIGHT - blob.r
                blob.vel.y = -blob.vel.y
            metaballs.append(blob.pos.x)
            metaballs.append(blob.pos.y)
            metaballs.append(blob.r)

        metaballs = numpy.array(metaballs, dtype=numpy.float32)

        display(shader, vertex_array_object, metaballs)
        pygame.display.set_caption("FPS: %.2f" % clock.get_fps())
        pygame.display.flip()


if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
