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
from MaterialLibrary import MaterialLibrary
import Shader
from Material import Material, FaceTypes
from Texture import Texture
from Transform import Transform
from Camera import Camera
from Quaternion import Quaternion
from Light import *
from Mesh import Mesh
from Skybox import Skybox

import yaml

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

        self.depthMapFBO = glGenFramebuffers(1)
        self.depthMap = glGenTextures(1)

        self.shadow_map_size = 2048

        self.sun = Light(np.array([1,1,1],"f"),1)
        self.sun.transform.translate(5, 10, 0)

        self.skybox = Skybox()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        
        glCullFace(GL_BACK)

        glClearColor(0.1, 0.2, 0.3, 1.0)


    def add_mesh(self, mesh):
        self.meshes.append(mesh)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.width, self.height)
        
        self.simple_draw(lit_shader)

        #self.debug()

    def simple_draw(self, shader):
        shader.use()

        for mesh in self.meshes:
            self.set_matrices(mesh, shader)
            mesh.draw()

    def shadow_map(self):
        glBindTexture(GL_TEXTURE_2D, self.depthMap)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.shadow_map_size, self.shadow_map_size, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depthMap, 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        lightProjection = self.sun.getLightProjection()
        lightView = self.sun.getLightView()

        lightSpaceMatrix = np.matmul(lightProjection, lightView)

        shadow_map_shader.use()
        glUniformMatrix4fv(shadow_map_shader.get_keyword("lightSpaceMatrix"), 1, GL_TRUE, lightSpaceMatrix)

        glViewport(0, 0, self.shadow_map_size, self.shadow_map_size)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)
        glClear(GL_DEPTH_BUFFER_BIT)
        
        self.simple_draw(shadow_map_shader)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)


    # method that supplies model, view and projection matrices to the shader
    def set_matrices(self, mesh, shader):
        shader.use()

        model_matrix = mesh.transform.getTRSMatrix()
        view_matrix = self.camera.getViewMatrix()
        projection_matrix = self.camera.projectionMatrix

        glUniformMatrix4fv(shader.get_keyword("model"), 1, GL_TRUE, model_matrix)
        glUniformMatrix4fv(shader.get_keyword("view"), 1, GL_TRUE, view_matrix)
        glUniformMatrix4fv(shader.get_keyword("projection"), 1, GL_TRUE, projection_matrix)

        # light uniforms
        glUniform3fv(shader.get_keyword("viewPos"), 1, self.camera.transform.position)
        glUniform3fv(shader.get_keyword("lightPos"), 1, self.sun.transform.position)
        # light space matrix
        lightSpaceMatrix = self.sun.getLightSpaceMatrix()
        glUniformMatrix4fv(shader.get_keyword("lightSpaceMatrix"), 1, GL_TRUE, lightSpaceMatrix)

        # shadow map
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.depthMap)
        glUniform1i(shader.get_keyword("shadowMap"), 0)

        glUniform3fv(shader.get_keyword("viewDir"), 1, self.camera.transform.forward())

        mesh.material.use(shader)
    
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
        self.sun.transform.position = np.array([np.cos(current_time()) * 5, 10, np.sin(current_time()) * 5])

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
            dt = 1.0 if fps == 0 else 1.0 / fps

            pygame.display.set_caption(f"FPS: {fps} ({dt*1000}ms)")

            # holding keys
            keys = pygame.key.get_pressed()
            
            # mouse delta
            mouse_delta = pygame.mouse.get_rel()

            # if mouse is held down
            if pygame.mouse.get_pressed()[0]:
                rotX = mouse_delta[0] * dt * 50
                rotY = mouse_delta[1] * dt * 50
                
                self.camera.rotate_local(rotY, rotX)

            #print(self.camera.transform.position, self.camera.transform.rotation)

            speed = 1.0 * dt

            # if holding left shift
            if keys[pygame.K_LSHIFT]:
                speed *= 5

            if keys[pygame.K_w]:
                self.camera.transform.position += self.camera.forward() * speed
            if keys[pygame.K_s]:
                self.camera.transform.position -= self.camera.forward() * speed
            if keys[pygame.K_a]:
                self.camera.transform.position += self.camera.right() * speed
            if keys[pygame.K_d]:
                self.camera.transform.position -= self.camera.right() * speed
            if keys[pygame.K_q]:
                self.camera.transform.position += self.camera.up() * speed
            if keys[pygame.K_e]:
                self.camera.transform.position -= self.camera.up() * speed

            self.update(dt)
            self.skybox.draw(skybox_shader, self.camera)
            self.shadow_map()
            self.draw()

            self.clock.tick(165)
            pygame.display.flip()

    def load_scene(self, path):
        with open(path, "r") as scene:
            scene_data = yaml.safe_load(scene)

            materials = {}

            # fetch materials
            for material_name in scene_data["Materials"]:
                material_data = scene_data["Materials"][material_name]
                
                texture_data = material_data["textures"]

                tiling = np.array(material_data["tiling"])

                mat = Material()
                mat.name = material_name

                mat.tiling = tiling

                mat.shader = lit_shader

                for tex_name, tex_path in texture_data.items():
                    tex = Texture(tex_path)
                    mat.add_texture(tex, tex_name)

                materials[material_name] = mat
                    

            # fetch meshes
            for mesh_name in scene_data["Meshes"]:
                mesh_data = scene_data["Meshes"][mesh_name]
                
                mesh = blender.load_mesh(mesh_data["path"])
                mesh.name = mesh_name
                
                mat_name = mesh_data["material"]
                mesh.set_material(materials[mat_name])

                mesh.transform.position = mesh_data["position"]

                rotX, rotY, rotZ = mesh_data["rotation"]
                mesh.transform.rotation = Quaternion.FromEuler(rotX, rotY, rotZ)

                mesh.transform.scale = mesh_data["scale"]

                recalculate_normals = mesh_data["recalculateNormals"]
                if recalculate_normals:
                    mesh.recalculate_normals()

                self.meshes.append(mesh)
                

def current_time():
    return time.time() - start_time


scene = Scene()

shadow_map_shader = Shader.Shader("shaders/shadow_map/shadow_vertex.glsl", "shaders/shadow_map/shadow_fragment.glsl")
lit_shader = Shader.Shader("shaders/basic/vertex.glsl", "shaders/basic/fragment.glsl")
skybox_shader = Shader.Shader("shaders/skybox/vertex.glsl", "shaders/skybox/fragment.glsl")

scene.load_scene("scene.yaml")

scene.run()