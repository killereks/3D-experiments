import pygame
import numpy

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import compileShader, compileProgram

import math

import time

start_time = time.time()

deltaTime = 0.0

def get_time():
    return time.time() - start_time
   
class Transform:
    def __init__(self, position, rotation):
        self.position = position
        self.rotation = rotation
       
    def forward(self):
        rotX = self.rotation[0] # pitch
        rotY = self.rotation[1] # yaw
        rotZ = self.rotation[2] # roll
       
        x = math.sin(rotY) * math.cos(rotX)
        y = math.sin(-rotX)
        z = math.cos(rotX) * math.cos(rotY)
       
        return numpy.array([x,y,z])
       
    def right(self):
        rotX = self.rotation[0] # pitch
        rotY = self.rotation[1] # yaw
        rotZ = self.rotation[2] # roll
       
        x = math.cos(rotY)
        y = 0
        z = -math.sin(rotY)
       
        return numpy.array([x,y,z])
       
    def up(self):
        return numpy.cross(self.forward(), self.right())
       
    def move(self, delta):
        self.position = numpy.add(self.position, delta)
       
    def rotate(self, delta):
        self.rotation = numpy.add(self.rotation, delta)
       
    def print(self):
        print("position", self.position,"rotation",self.rotation)

class RayTracer:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        gluPerspective(45, (self.width / self.height), 0.1, 50.0)

        self.shader = Shader("shaders/vertex.glsl", "shaders/fragment.glsl")
        self.shader.use()
       
        cameraPos = numpy.array([0,1,-3])
        cameraRot = numpy.array([0,0,0])
       
        self.cameraT = Transform(cameraPos, cameraRot)

        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(165)
            deltaTime = self.clock.get_fps() / 1000.0
            self.handle_events(deltaTime)
            self.update()
            self.draw()
           
            self.cameraT.print()

            #display fps
            pygame.display.set_caption("FPS: " + str(self.clock.get_fps()))

    def handle_events(self, deltaTime):
        # get keys
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        fwd = self.cameraT.forward()
        right = self.cameraT.right()
        up = self.cameraT.up()

        speed = 1.0

        # if left shift
        if keys[pygame.K_LSHIFT]:
            speed = 10.0

        if keys[pygame.K_w]:
            self.cameraT.move(fwd * speed * deltaTime)
        if keys[pygame.K_s]:
            self.cameraT.move(fwd * -speed * deltaTime)
        if keys[pygame.K_a]:
            self.cameraT.move(right * -speed * deltaTime)
        if keys[pygame.K_d]:
            self.cameraT.move(right * speed * deltaTime)
        if keys[pygame.K_e]:
            self.cameraT.move(up * speed * deltaTime)
        if keys[pygame.K_q]:
            self.cameraT.move(up * -speed * deltaTime)

        mouseDelta = pygame.mouse.get_rel()
        # is mouse held down
        if pygame.mouse.get_pressed()[0]:
            deltaX, deltaY = mouseDelta[0], mouseDelta[1]
        
            rotation = numpy.array([deltaY, deltaX, 0])
            self.cameraT.rotate(rotation * 0.01)

    def update(self):
        cameraPos = self.cameraT.position
       
        cameraFwd = self.cameraT.forward()
        cameraRight = self.cameraT.right()
   
        glUniform1f(glGetUniformLocation(self.shader.program, "time"), get_time())
        glUniform2f(glGetUniformLocation(self.shader.program, "resolution"), self.width, self.height)
       
        glUniform3f(glGetUniformLocation(self.shader.program, "cameraPos"), cameraPos[0], cameraPos[1], cameraPos[2])
        glUniform3f(glGetUniformLocation(self.shader.program, "cameraFwd"), cameraFwd[0], cameraFwd[1], cameraFwd[2])
        glUniform3f(glGetUniformLocation(self.shader.program, "cameraRight"), cameraRight[0], cameraRight[1], cameraRight[2])

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