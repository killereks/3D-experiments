# imports all openGL functions
from OpenGL.GL import *

#import glu
from OpenGL.GLU import *

# pygame is just used to create a window with the operating system on which to draw.
import pygame

# we will use numpy to store data in arrays
import numpy as np

import time

import pyrr

import blender
import MaterialLibrary
import Shader
from Transform import Transform
from Camera import Camera

from custom_logging import LOG, LogLevel

start_time = time.time()

pygame.init()

class Scene:
    def __init__(self):
        self.width = 800
        self.height = 600

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF, 24)

        self.clock = pygame.time.Clock()

        self.running = True

        self.meshes = []

        self.camera = Camera(60, 0.1, 1000)

        gluPerspective(60, self.width / self.height, 0.1, 1000)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        glShadeModel(GL_SMOOTH)

        glTranslatef(0.0, 0.0, -10)

        glViewport(0, 0, self.width, self.height)

        glClearColor(0.2, 0.3, 0.2, 1.0)


    def add_mesh(self, mesh):
        self.meshes.append(mesh)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for mesh in self.meshes:
            self.set_matrices(mesh)
            mesh.draw()

    # method that supplies model, view and projection matrices to the shader
    def set_matrices(self, mesh):
        # set model matrix
        #glUniformMatrix4fv(glGetUniformLocation(shader.program, "model"), 1, GL_FALSE, mesh.transform.getTRSMatrix())

        # set view matrix
        #glUniformMatrix4fv(glGetUniformLocation(shader.program, "view"), 1, GL_FALSE, self.camera.getViewMatrix())

        # set projection matrix
        #glUniformMatrix4fv(glGetUniformLocation(shader.program, "projection"), 1, GL_FALSE, self.camera.projectionMatrix)

        model_matrix = mesh.transform.getTRSMatrix()
        view_matrix = self.camera.getViewMatrix()
        projection_matrix = self.camera.projectionMatrix

        model_matrix = np.identity(4)
        view_matrix = np.identity(4)
        projection_matrix = np.identity(4)

        glUniformMatrix4fv(glGetUniformLocation(shader.program, "model"), 1, GL_FALSE, model_matrix)
        glUniformMatrix4fv(glGetUniformLocation(shader.program, "view"), 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(shader.program, "projection"), 1, GL_FALSE, projection_matrix)
        #glUniformMatrix4fv(glGetUniformLocation(shader.program, "PVM"), 1, GL_FALSE, PVM)

    def update(self):
        # set current shader time
        glUniform1f(glGetUniformLocation(shader.program, "time"), current_time())


    def run(self):
        while self.running:
            # handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    LOG("Quitting...", LogLevel.CRITICAL)
                    self.running = False

            # holding keys
            keys = pygame.key.get_pressed()
            
            # mouse delta
            mouse_delta = pygame.mouse.get_rel()

            # if mouse is held down
            if pygame.mouse.get_pressed()[0]:
                rotX = mouse_delta[0] * 0.1
                rotY = mouse_delta[1] * 0.1

                self.camera.transform.rotate(rotY, rotX, 0)

            #print(self.camera.transform.position, self.camera.transform.rotation)

            #W
            if keys[pygame.K_w]:
                self.camera.transform.position += self.camera.transform.forward() * 0.1
            #S
            if keys[pygame.K_s]:
                self.camera.transform.position -= self.camera.transform.forward() * 0.1
            #A
            if keys[pygame.K_a]:
                self.camera.transform.position -= self.camera.transform.right() * 0.1
            #D
            if keys[pygame.K_d]:
                self.camera.transform.position += self.camera.transform.right() * 0.1
            #E
            if keys[pygame.K_e]:
                self.camera.transform.position += self.camera.transform.up() * 0.1
            #Q
            if keys[pygame.K_q]:
                self.camera.transform.position -= self.camera.transform.up() * 0.1

            self.clock.tick(165)
            # display fps
            pygame.display.set_caption("FPS: " + str(self.clock.get_fps()))

            self.update()
            self.draw()

            pygame.display.flip()

def current_time():
    return time.time() - start_time


scene = Scene()

shader = Shader.Shader("shaders/basic/vertex.glsl", "shaders/basic/fragment.glsl")
shader.use()

monkey_mesh = blender.load_mesh("models/monkey/monkey.obj")
scene.add_mesh(monkey_mesh)

#car_mesh = blender.load_mesh('models/car/audi r8.obj')
#scene.add_mesh(car_mesh)

scene.run()