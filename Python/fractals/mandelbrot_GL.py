from pathlib import Path
from OpenGL.GL import *
import ctypes
import pygame
import numpy
from ShaderLoader import compile_shader

user32 = ctypes.windll.user32
SCREEN_WIDTH = user32.GetSystemMetrics(0)
SCREEN_HEIGHT = user32.GetSystemMetrics(1)

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

    # Send the data over to the buffers
    glBufferData(GL_ARRAY_BUFFER, 32, vertices, GL_STATIC_DRAW)  # Vertices array
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, 24, indices, GL_STATIC_DRAW)  # Indices array

    # Unbind the VAO first (Important)
    glBindVertexArray(0)

    # Unbind other stuff
    glDisableVertexAttribArray(position)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    return vertex_array_object


def display(shader, vertex_array_object, data_for_gpu, offset, real_min, real_max, imag_min, imag_max):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glUseProgram(shader)

    screen_width_loc = glGetUniformLocation(shader, "screen_width")
    glUniform1f(screen_width_loc, SCREEN_WIDTH)
    screen_height_loc = glGetUniformLocation(shader, "screen_height")
    glUniform1f(screen_height_loc, SCREEN_HEIGHT)

    real_min_loc = glGetUniformLocation(shader, "real_min")
    glUniform1f(real_min_loc, real_min)
    real_max_loc = glGetUniformLocation(shader, "real_max")
    glUniform1f(real_max_loc, real_max)

    imag_min_loc = glGetUniformLocation(shader, "imag_min")
    glUniform1f(imag_min_loc, imag_min)
    imag_max_loc = glGetUniformLocation(shader, "imag_max")
    glUniform1f(imag_max_loc, imag_max)

    offset_loc = glGetUniformLocation(shader, "col_offset")
    glUniform1i(offset_loc, offset)

    colour_map_loc = glGetUniformLocation(shader, "colour_map")
    glUniform3fv(colour_map_loc, int(len(data_for_gpu) / 3), data_for_gpu)

    glBindVertexArray(vertex_array_object)
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)  # Replaces glDrawArrays because we're drawing indices now.
    glBindVertexArray(0)

    glUseProgram(0)


def draw_text(x, y, text):
    position = (x, y)
    font = pygame.font.SysFont('arial', 20)
    text_surface = font.render(text, True, (0, 0, 255, 255)).convert_alpha()
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(*position)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)


def main():
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    glClearColor(0.0, 0.0, 0.1, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    shader = compile_shader(Path('shaders', 'fractal.vert'),
                            Path('shaders', 'mandelbrot.frag'))

    vertex_array_object = create_object(shader)

    reds = []
    yellows = []
    whites = []
    for i in range(64):
        reds.extend([i * 4 / 255, 0.0, 0.0])
        yellows.extend([1.0, i * 4 / 255, 0.0])
        whites.extend([1.0, 1.0, i * 4 / 255])
    whites.extend([1.0, 1.0, 1.0])

    col_map = reds + yellows + whites
    colour_map = numpy.array(col_map, dtype=numpy.float32)

    x_min = -2.5
    x_max = 1.5
    y_min = -1.5
    y_max = 1.5
    x_zoom = (x_max - x_min) * 0.1
    y_zoom = (y_max - y_min) * 0.1
    colour_cycle = False
    offset = 0
    show_help = False
    help_string = """Keys:
    Space: colour cycle on/off
    L arrow: decrease X min
    R arrow: increase X min
    U arrow: increase Y min
    D arrow: decrease Y min
    KP1 arrow: decrease X max
    KP3 arrow: increase X max
    KP5 arrow: increase Y max
    KP2 arrow: decrease Y max"""

    clock = pygame.time.Clock()

    while True:
        clock.tick(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_F1:
                    show_help = not show_help
                elif event.key == pygame.K_SPACE:
                    colour_cycle = not colour_cycle
                elif event.key == pygame.K_LEFT:
                    x_min -= x_zoom
                elif event.key == pygame.K_RIGHT:
                    x_min += x_zoom
                elif event.key == pygame.K_UP:
                    y_min += y_zoom
                elif event.key == pygame.K_DOWN:
                    y_min -= y_zoom
                elif event.key == pygame.K_KP1:
                    x_max -= x_zoom
                elif event.key == pygame.K_KP3:
                    x_max += x_zoom
                elif event.key == pygame.K_KP5:
                    y_max += y_zoom
                elif event.key == pygame.K_KP2:
                    y_max -= y_zoom
            x_zoom = (x_max - x_min) * 0.1
            y_zoom = (y_max - y_min) * 0.1

        display(shader, vertex_array_object, colour_map, offset, x_min, x_max, y_min, y_max)
        if colour_cycle:
            offset = (offset + 1) % len(colour_map)
        else:
            offset = 0

        draw_text(10,
                  SCREEN_HEIGHT - 225 if show_help else SCREEN_HEIGHT - 20,
                  help_string if show_help else "F1 for help")

        pygame.display.set_caption("FPS: %.2f" % clock.get_fps())
        pygame.display.flip()


if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
