import pygame
import numpy
from OpenGL.GL import *
from OpenGL.GLU import *

import time

from OpenGL.GL.shaders import compileShader, compileProgram

start_time = time.time()

def get_time():
    return time.time() - start_time

class RayTracer:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        gluPerspective(45, (self.width / self.height), 0.1, 50.0)

        self.shader = Shader("shaders/vertex.glsl", "shaders/fragment.glsl")
        self.shader.use()

        self.cameraPos = numpy.array([0.0, 1.0, -3.0])
        self.cameraDir = numpy.array([0.0, 0.0, 1.0])

        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(165)
            self.handle_events()
            self.update()
            self.draw()

            #display fps
            pygame.display.set_caption("FPS: " + str(self.clock.get_fps()))

    def handle_events(self):
        # get keys
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        if keys[pygame.K_w]:
            self.cameraPos += self.cameraDir * 0.1
        if keys[pygame.K_s]:
            self.cameraPos -= self.cameraDir * 0.1
        if keys[pygame.K_a]:
            self.cameraPos += numpy.cross(self.cameraDir, numpy.array([0.0, 1.0, 0.0])) * 0.1
        if keys[pygame.K_d]:
            self.cameraPos -= numpy.cross(self.cameraDir, numpy.array([0.0, 1.0, 0.0])) * 0.1
        if keys[pygame.K_e]:
            self.cameraPos += numpy.array([0.0, 1.0, 0.0]) * 0.1
        if keys[pygame.K_q]:
            self.cameraPos -= numpy.array([0.0, 1.0, 0.0]) * 0.1
            



    def update(self):
        glUniform1f(glGetUniformLocation(self.shader.program, "time"), get_time())
        glUniform2f(glGetUniformLocation(self.shader.program, "resolution"), self.width, self.height)
        glUniform3f(glGetUniformLocation(self.shader.program, "cameraPos"), self.cameraPos[0], self.cameraPos[1], self.cameraPos[2])
        glUniform3f(glGetUniformLocation(self.shader.program, "cameraDir"), self.cameraDir[0], self.cameraDir[1], self.cameraDir[2])

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        glColor3f(1.0, 1.0, 1.0)

        size = 1.0

        # draw a quad with the shader
        glBegin(GL_QUADS)
        glVertex2f(-size, -size)
        glVertex2f(size, -size)
        glVertex2f(size, size)
        glVertex2f(-size, size)
        glEnd()

        pygame.display.flip()

class Shader:
    def __init__(self, vertexFile, fragmentFile):
        with open(vertexFile, "r") as f:
            vertexSource = f.read()

        with open(fragmentFile, "r") as f:
            fragmentSource = f.read()

        vertexShader = compileShader(vertexSource, GL_VERTEX_SHADER)
        fragmentShader = compileShader(fragmentSource, GL_FRAGMENT_SHADER)
        
        # see if there are any errors
        vCompileStatus = glGetShaderiv(vertexShader, GL_COMPILE_STATUS)
        if vCompileStatus != GL_TRUE:
            print(glGetShaderInfoLog(vertexShader))
            raise Exception("Vertex shader compilation failed.")

        fCompileStatus = glGetShaderiv(fragmentShader, GL_COMPILE_STATUS)
        if fCompileStatus != GL_TRUE:
            print(glGetShaderInfoLog(fragmentShader))
            raise Exception("Fragment shader compilation failed.")

        self.program = compileProgram(vertexShader, fragmentShader)

    def use(self):
        glUseProgram(self.program)

if __name__ == "__main__":
    rt = RayTracer()
    rt.run()
