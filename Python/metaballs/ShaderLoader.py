from pathlib import WindowsPath

from OpenGL.GL import *
import OpenGL.GL.shaders


def load_shader(shader_file):
    with open(shader_file) as f:
        shader_source = f.read()
    f.close()
    return str.encode(shader_source)


def compile_shader(vs, fs):
    vert_shader = load_shader(vs) if type(vs) is WindowsPath else vs
    frag_shader = load_shader(fs) if type(fs) is WindowsPath else fs

    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(vert_shader, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(frag_shader, GL_FRAGMENT_SHADER))
    return shader
