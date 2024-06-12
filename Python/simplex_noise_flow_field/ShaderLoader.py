from OpenGL.GL import *
import OpenGL.GL.shaders


def load_shader(shader_file):
    with open(shader_file) as f:
        shader_source = f.readlines()
    f.close()
    if shader_source[0].startswith('#version'):
        return str.encode(shader_source[0]), str.encode(''.join(shader_source[1:]))
    else:
        return str.encode(''.join(shader_source))


def compile_shader(vs, fs, includes=None):
    vv, vert_shader = load_shader(vs)
    fv, frag_shader = load_shader(fs)
    if includes is not None:
        try:
            vert_includes = includes["vertex"]
            for vert_incl in vert_includes:
                incl = load_shader(vert_incl)
                vert_shader = incl + b'\n\n' + vert_shader
            vert_shader = vv + vert_shader
            frag_includes = includes["fragment"]
            for frag_incl in frag_includes:
                incl = load_shader(frag_incl)
                frag_shader = incl + b'\n\n' + frag_shader
            frag_shader = fv + frag_shader
        except KeyError as e:
            print(e)

    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(vert_shader, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(frag_shader, GL_FRAGMENT_SHADER))
    return shader
