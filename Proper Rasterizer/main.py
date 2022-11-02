# imports all openGL functions
from OpenGL.GL import *

#import glu
from OpenGL.GLU import *

# pygame is just used to create a window with the operating system on which to draw.
import pygame

# we will use numpy to store data in arrays
import numpy as np

import time

import blender
import MaterialLibrary
import Shader
from Material import Material, FaceTypes
from Texture import Texture
from Transform import Transform
from Camera import Camera

from custom_logging import LOG, LogLevel

start_time = time.time()

pygame.init()

class Scene:
    def __init__(self):
        self.width = 1024
        self.height = 768

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF, 24)

        self.clock = pygame.time.Clock()

        self.running = True

        self.meshes = []

        aspect = self.width / self.height

        self.camera = Camera(80, aspect, 0.1, 100)
        self.camera.transform.translate(0, -2, -2)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        
        glCullFace(GL_BACK)

        glClearColor(0.1, 0.2, 0.3, 1.0)


    def add_mesh(self, mesh):
        self.meshes.append(mesh)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        lit_shader.use()
        for mesh in self.meshes:
            self.set_matrices(mesh)
            mesh.draw()

        self.debug()

    def debug(self):
        unlit_shader.use()
        # draw forward, right and up vectors from the origin
        self.draw_axes()
        
    def draw_axes(self):
        glUniformMatrix4fv(unlit_shader.get_keyword("model"), 1, GL_FALSE, np.identity(4))
        glUniformMatrix4fv(unlit_shader.get_keyword("view"), 1, GL_FALSE, self.camera.getViewMatrix())
        glUniformMatrix4fv(unlit_shader.get_keyword("projection"), 1, GL_FALSE, self.camera.projectionMatrix)

        LENGTH = 2

        glBegin(GL_LINES)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(LENGTH, 0, 0)

        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, LENGTH, 0)

        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, LENGTH)

        glEnd()


    # method that supplies model, view and projection matrices to the shader
    def set_matrices(self, mesh):
        model_matrix = mesh.transform.getTRSMatrix()
        view_matrix = self.camera.getViewMatrix()
        projection_matrix = self.camera.projectionMatrix

        glUniformMatrix4fv(lit_shader.get_keyword("model"), 1, GL_FALSE, model_matrix)
        glUniformMatrix4fv(lit_shader.get_keyword("view"), 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(lit_shader.get_keyword("projection"), 1, GL_FALSE, projection_matrix)

        mat = mesh.material
        glUniform1f(mat.shader.get_keyword("time"), current_time())

        self.set_face_culling(mat.face_type)
        
        mat.use()
    
    def set_face_culling(self, cull_face_type):
        if cull_face_type == FaceTypes.CULL_BACK:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
        elif cull_face_type == FaceTypes.CULL_FRONT:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_FRONT)
        elif cull_face_type == FaceTypes.CULL_NONE:
            glDisable(GL_CULL_FACE)


    def update(self, dt):
        # set current shader time

        for mesh in self.meshes:
            mesh.update(dt)


    def run(self):
        while self.running:
            # handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    LOG("Quitting...", LogLevel.CRITICAL)
                    self.running = False

            fps = self.clock.get_fps()
            pygame.display.set_caption("FPS: " + str(fps))

            dt = 1.0 if fps == 0 else 1.0 / fps

            # holding keys
            keys = pygame.key.get_pressed()
            
            # mouse delta
            mouse_delta = pygame.mouse.get_rel()

            # if mouse is held down
            if pygame.mouse.get_pressed()[0]:
                rotX = mouse_delta[0] * dt * 10
                rotY = mouse_delta[1] * dt * 10
                
                self.camera.rotate(rotY, rotX, 0)

            #print(self.camera.transform.position, self.camera.transform.rotation)

            speed = 1.0 * dt

            if keys[pygame.K_w]:
                self.camera.transform.position += self.camera.transform.forward() * speed
            if keys[pygame.K_s]:
                self.camera.transform.position -= self.camera.transform.forward() * speed
            if keys[pygame.K_a]:
                self.camera.transform.position += self.camera.transform.right() * speed
            if keys[pygame.K_d]:
                self.camera.transform.position -= self.camera.transform.right() * speed
            if keys[pygame.K_q]:
                self.camera.transform.position += self.camera.transform.up() * speed
            if keys[pygame.K_e]:
                self.camera.transform.position -= self.camera.transform.up() * speed

            self.update(dt)
            self.draw()

            self.clock.tick(165)
            pygame.display.flip()

def current_time():
    return time.time() - start_time


scene = Scene()

lit_shader = Shader.Shader("shaders/basic/vertex.glsl", "shaders/basic/fragment.glsl")
unlit_shader = Shader.Shader("shaders/unlit/vertex.glsl", "shaders/unlit/fragment.glsl")

texture = Texture("textures/checkerboard.png")

material = Material(lit_shader)
material.add_texture(texture)

monkey_mesh = blender.load_mesh("models/monkey/monkey.obj")
monkey_mesh.recalculate_normals()
monkey_mesh.set_material(material)

floor_mesh = blender.load_mesh("models/floor/floor.obj")
floor_mesh.recalculate_normals()
floor_mesh.set_material(material)

scene.add_mesh(monkey_mesh)
scene.add_mesh(floor_mesh)

#floor_mesh = blender.load_mesh("models/floor/floor.obj")
#floor_mesh.recalculate_normals()
#scene.add_mesh(floor_mesh)

#torus_mesh = blender.load_mesh("models/torus/torus.obj")
#torus_mesh.recalculate_normals()
#scene.add_mesh(torus_mesh)

#car_mesh = blender.load_mesh('models/car/audi r8.obj')
#scene.add_mesh(car_mesh)

scene.run()