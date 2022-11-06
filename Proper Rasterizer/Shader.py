from OpenGL.GL import *

from OpenGL.GL.shaders import compileShader, compileProgram

class Shader:
    def __init__(self, vertex_path: str, fragment_path: str):
        
        with open(vertex_path, "r") as file:
            vertex_src = file.read()

        with open(fragment_path, "r") as file:
            fragment_src = file.read()
            
        vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)

        self.program = compileProgram(vertex_shader, fragment_shader)
        
    def use(self):
        """
        Use the shader
        """
        glUseProgram(self.program)

    def get_keyword(self, keyword):
        """
        Get the location of a keyword in the shader
        """
        return glGetUniformLocation(self.program, keyword)