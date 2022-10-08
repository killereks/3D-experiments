

# imports all openGL functions
from OpenGL.GL import *

# pygame is just used to create a window with the operating system on which to draw.
import pygame

# we will use numpy to store data in arrays
import numpy as np

import time

# initialize pygame and opengl

pygame.init()
pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

class Scene:
    def __init__(self):
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def draw(self):
        for obj in self.objects:
            obj.draw()

class Triangle:
    def __init__(self, vertices, colors):
        self.vertices = vertices
        self.colors = colors

        self.shader = glCreateProgram()
        self.vbo = glGenBuffers(1)
        self.vao = glGenVertexArrays(1)

        self.compile_shader()

    def compile_shader(self):
        # create a shader program
        shader = self.shader

        # create vertex shader
        vshader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vshader, VSHADER)
        glCompileShader(vshader)

        # create fragment shader
        fshader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fshader, FSHADER)
        glCompileShader(fshader)

        # attach shaders to shader program
        glAttachShader(shader, vshader)
        glAttachShader(shader, fshader)

        # link shader program
        glLinkProgram(shader)

        # delete shaders
        glDeleteShader(vshader)
        glDeleteShader(fshader)

    def draw(self):
        # use shader program
        glUseProgram(self.shader)

        # bind vertex array object
        glBindVertexArray(self.vao)

        # bind vertex buffer object
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # copy data to vertex buffer object
        data = np.concatenate((self.vertices, self.colors), axis=1).flatten()
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

        # set vertex attribute pointers
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        # draw triangle
        glDrawArrays(GL_TRIANGLES, 0, 3)

        # unbind vertex array object
        glBindVertexArray(0)

        # unuse shader program
        glUseProgram(0)


# vertex shader
VSHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
out vec3 color;
void main()
{
    gl_Position = vec4(aPos, 1.0);
    color = aColor;
}
"""

# fragment shader
FSHADER = """
#version 330 core
out vec4 FragColor;
in vec3 color;

void main()
{
    FragColor = vec4(color, 1.0);
}
"""

scene = Scene()
obj1 = Triangle(np.array([[-0.5, -0.5, 0.0], [0.5, -0.5, 0.0], [0.0, 0.5, 0.0]]), np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]))

scene.add_object(obj1)


while True:
    # clear the screen
    glClear(GL_COLOR_BUFFER_BIT)
    
    scene.draw()

    #display fps
    pygame.display.set_caption("fps: " + str(clock.get_fps()))
    clock.tick(100)

    # swap the buffers
    pygame.display.flip()

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()