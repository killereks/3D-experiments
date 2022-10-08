

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

start_time = time.time()

def current_time():
    return time.time() - start_time

FSHADER = """
#version 330 core

in vec3 color;
out vec4 fragColor;

void main()
{
    fragColor = vec4(color, 1.0);
}
"""

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

while True:
    # clear the screen
    glClear(GL_COLOR_BUFFER_BIT)
    
    # create a shader program
    shader = glCreateProgram()

    # create the vertex shader
    vshader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vshader, VSHADER)
    glCompileShader(vshader)
    glAttachShader(shader, vshader)

    # create the fragment shader
    fshader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fshader, FSHADER)
    glCompileShader(fshader)
    glAttachShader(shader, fshader)

    # link the shader program
    glLinkProgram(shader)
    glUseProgram(shader)

    size = 0.9

    # create the vertex data for a quad filling screen
    vertices = np.array([
        -size, -size, 0.0, 1.0, 0.0, 0.0,
        size, -size, 0.0, 0.0, 1.0, 0.0,
        size, size, 0.0, 0.0, 0.0, 1.0,
        -size, size, 0.0, 1.0, 1.0, 1.0
    ], dtype=np.float32)

    # create the vertex buffer object
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # create the vertex array object
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # set the vertex attributes
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    # draw the quad
    glDrawArrays(GL_QUADS, 0, 4)

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