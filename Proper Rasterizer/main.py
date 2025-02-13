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
import Shader
from Material import Material, FaceTypes
from Texture import Texture
from Camera import Camera
from Quaternion import Quaternion
from Light import *
from Mesh import Mesh
from Skybox import Skybox
from PostProcessing import PostProcessing
from Water import Water

from Programs import Programs
from InstancedField import InstancedField

from MathUtils import *

import random

import yaml

from custom_logging import LOG, LogLevel

from PIL import Image

start_time = time.time()

pygame.init()

initialized = False

class Scene:
    def __init__(self):
        self.width = 1920#1024
        self.height = 1080#768

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF, 32)

        self.clock = pygame.time.Clock()

        self.running = True

        self.meshes = []

        aspect = self.width / self.height

        self.camera = Camera(80, aspect, 0.1, 500)
        # handpicked location for the camera
        self.camera.transform.position = np.array([151.1606,-36.485424,-34.45971], "f")

        self.depthMapFBO = glGenFramebuffers(1)
        self.depthMap = glGenTextures(1)

        self.cameraDepthMapFBO = glGenFramebuffers(1)
        self.cameraDepthMap = glGenTextures(1)

        self.shadow_map_size = 4096

        self.sun = Light(np.array([1,1,1],"f"),1)
        #self.sun.transform.position = np.array([-150, 150, -150], "f")

        self.timeOfDay = 8

        self.calculateSun()

        self.skybox = Skybox()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        
        glCullFace(GL_BACK)

        glClearColor(0.1, 0.2, 0.3, 1.0)

        # enable transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # initialize shadow map
        self.initialize_shadow_map()
        self.initialize_camera_depth_map()

        self.debugview = 0
        

    def initialize_shadow_map(self):
        """
        Initializes the shadow map texture and framebuffer.
        """
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

    def initialize_camera_depth_map(self):
        """
        Initializes the camera depth map texture and framebuffer.
        """
        glBindTexture(GL_TEXTURE_2D, self.cameraDepthMap)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glBindFramebuffer(GL_FRAMEBUFFER, self.cameraDepthMapFBO)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.cameraDepthMap, 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)


    def add_mesh(self, mesh: Mesh):
        """
        Adds a mesh to the scene

        :param mesh: The mesh instance to add
        """
        self.meshes.append(mesh)

    def draw_scene(self, shader: Shader):
        """
        Draws the scene using the given shader.
        Shader needs to have a model, view and projection matrix uniform.

        This is used for the shadow map pass and the main draw pass, so shader is flexible.
        
        :param shader: Override shader to use for drawing
        """
        if shader is not None:
            shader.use()

        for mesh in self.meshes:
            self.set_matrices(mesh, shader)
            if shader == None:
                mesh.shader.use()
            mesh.draw()

    def shadow_map(self):
        global initialized
        """
        Renders the scene from the light's perspective to a depth map.
        
        This is used to determine which fragments are in shadow.
        """
        #glCullFace(GL_FRONT)

        glBindTexture(GL_TEXTURE_2D, self.depthMap)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)

        lightProjection = self.sun.getLightProjection()
        lightView = self.sun.getLightView()

        lightSpaceMatrix = np.matmul(lightProjection, lightView)

        shadow_map_shader.use()
        glUniformMatrix4fv(shadow_map_shader.get_keyword("lightSpaceMatrix"), 1, GL_TRUE, lightSpaceMatrix)

        glViewport(0, 0, self.shadow_map_size, self.shadow_map_size)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)
        glClear(GL_DEPTH_BUFFER_BIT)
        
        self.draw_scene(shadow_map_shader)
        tree_field.draw(shadow_map_trees_shader, current_time(), True, 0)

        # save depthMap to file
        if not initialized:
            data = glReadPixels(0, 0, self.shadow_map_size, self.shadow_map_size, GL_DEPTH_COMPONENT, GL_FLOAT)
            data = np.flip(data, 0)
            data = np.flip(data, 1)
            data = np.reshape(data, (self.shadow_map_size, self.shadow_map_size))
            data = data * 255
            data = data.astype(np.uint8)
            im = Image.fromarray(data)
            im.save("depthMap.png")
            LOG(f"Saved depthMap to file", 3)
            initialized = True

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        #glCullFace(GL_BACK)

    def camera_depth(self):
        """
        Renders the depth of the scene from the camera's perspective.
        This is used for post processing effects.
        """
        glBindTexture(GL_TEXTURE_2D, self.cameraDepthMap)
        glBindFramebuffer(GL_FRAMEBUFFER, self.cameraDepthMapFBO)

        camera_depth_shader.use()
        glUniformMatrix4fv(camera_depth_shader.get_keyword("view"), 1, GL_TRUE, self.camera.transform.getTRSMatrix())
        glUniformMatrix4fv(camera_depth_shader.get_keyword("projection"), 1, GL_TRUE, self.camera.projectionMatrix)

        glViewport(0, 0, self.width, self.height)
        glBindFramebuffer(GL_FRAMEBUFFER, self.cameraDepthMapFBO)
        glClear(GL_DEPTH_BUFFER_BIT)

        self.draw_scene(camera_depth_shader)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)


    # method that supplies model, view and projection matrices to the shader
    def set_matrices(self, mesh: Mesh, shader: Shader):
        """
        Sets the model, view and projection matrices for the given shader.
        
        :param mesh: The mesh to get the model matrix from
        :param shader: The shader to set the matrices for
        """
        shader.use()

        model_matrix = mesh.transform.getTRSMatrix()
        view_matrix = self.camera.getViewMatrix()
        projection_matrix = self.camera.projectionMatrix

        glUniformMatrix4fv(shader.get_keyword("model"), 1, GL_TRUE, model_matrix)
        glUniformMatrix4fv(shader.get_keyword("view"), 1, GL_TRUE, view_matrix)
        glUniformMatrix4fv(shader.get_keyword("projection"), 1, GL_TRUE, projection_matrix)

        # light uniforms
        normalizedLightDir = -self.sun.transform.position / np.linalg.norm(self.sun.transform.position)
        glUniform3fv(shader.get_keyword("lightPos"), 1, self.sun.transform.position)
        glUniform3fv(shader.get_keyword("lightDir"), 1, normalizedLightDir)
        glUniform3fv(shader.get_keyword("sunColor"), 1, self.sun.color)

        # light space matrix
        lightSpaceMatrix = self.sun.getLightSpaceMatrix()
        glUniformMatrix4fv(shader.get_keyword("lightSpaceMatrix"), 1, GL_TRUE, lightSpaceMatrix)

        # shadow map (index 0)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.depthMap)
        glUniform1i(shader.get_keyword("shadowMap"), 0)

        glActiveTexture(GL_TEXTURE10)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.skybox.cubeMap)
        glUniform1i(shader.get_keyword("_Skybox"), 10)

        glActiveTexture(GL_TEXTURE11)
        glBindTexture(GL_TEXTURE_2D, self.cameraDepthMap)
        glUniform1i(shader.get_keyword("cameraDepthMap"), 11)

        # camera
        glUniform3fv(shader.get_keyword("camPos"), 1, -self.camera.transform.position)
        glUniform3fv(shader.get_keyword("camFwd"), 1, -self.camera.forward())

        mesh.material.use(shader)

        glUniform1f(shader.get_keyword("time"), current_time())
    
    def set_face_culling(self, cull_face_type: int):
        """
        Sets the face culling type.
        In most cases this should be GL_BACK, but if you want to draw the inside of a mesh, use GL_FRONT.
        
        :param cull_face_type: The face culling type
        """
        if cull_face_type == FaceTypes.CULL_BACK:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
        elif cull_face_type == FaceTypes.CULL_FRONT:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_FRONT)
        elif cull_face_type == FaceTypes.CULL_NONE:
            glDisable(GL_CULL_FACE)


    def update(self, dt: float):
        """
        Updates the scene.

        :param dt: Delta time, the time since the last frame, used to make updates framerate independent
        """
        #self.sun.transform.position = np.array([np.cos(current_time()) * 10, 2, np.sin(current_time()) * 10])

        self.debugView()

        for mesh in self.meshes:
            if mesh.isIcon:
                #mesh.transform.position = self.sun.transform.position
                #mesh.transform.lookAt(np.array([np.sin(current_time()),0,np.cos(current_time())]), np.array([0, 1, 0]))
                # rotate to look at camera
                mesh.transform.lookAtSelf(-self.camera.transform.position, np.array([0, 1, 0]))
                mesh.transform.rotateAxis(np.array([0, 1, 0]), 90)
                mesh.transform.rotateAxis(np.array([1,0,0]), -90)

            mesh.update(dt)

        self.get_mesh("sunIcon").transform.position = self.sun.transform.position

        #self.meshes[0].transform.position = self.sun.transform.position

    def debugView(self):
        """
        Allows user to click numbers from 0 to 9 to select drawing mode.
        """
        # pygame get key pressed
        keys = pygame.key.get_pressed()

        key_map = {
            pygame.K_0: 0,
            pygame.K_1: 1,
            pygame.K_2: 2,
            pygame.K_3: 3,
            pygame.K_4: 4,
            pygame.K_5: 5,
            pygame.K_6: 6,
            pygame.K_7: 7,
            pygame.K_8: 8,
            pygame.K_9: 9
        }

        for key in key_map:
            if keys[key]:
                self.debugview = key_map[key]

        # plus on keypad
        if keys[pygame.K_KP_PLUS]:
            self.timeOfDay += 0.03
            self.timeOfDay %= 24

            self.calculateSun()
        
        # minus on keypad
        if keys[pygame.K_KP_MINUS]:
            self.timeOfDay -= 0.03
            self.timeOfDay %= 24

            self.calculateSun()

    def calculateSun(self):
        """
        Calculates the sun's position based on the time of day. And the sun's color.
        """

        # calculate sun position
        #self.sun.transform.position = np.array([np.cos(self.timeOfDay / 24 * 2 * np.pi) * 150, 100, np.sin(self.timeOfDay / 24 * 2 * np.pi) * 150])

        x = np.sin(self.timeOfDay / 24 * 2 * np.pi) * 150
        y = -np.cos(self.timeOfDay / 24 * 2 * np.pi) * 150
        z = np.cos(self.timeOfDay / 24 * 2 * np.pi) * 50

        # calculate sun color
        sunColor = np.array([1, 1, 1])

        full_bright = np.array([1, 1, 1])
        full_dark = np.array([0.1, 0.1, 0.1])
        orange = np.array([1, 0.5, 0.1])
        
        # 9 to 18, full brightness [1,1,1]
        # 18 to 22, orange [1,0.5,0]
        # 22 to 23, black
        # 23 to 24, black
        # 0 to 5, black
        # 5 to 9, orange
        
        if self.timeOfDay >= 9 and self.timeOfDay < 18:
            perc = MathUtils.InverseLerp(9, 18, self.timeOfDay)
            sunColor = full_bright
        elif self.timeOfDay >= 18 and self.timeOfDay < 22:
            perc = MathUtils.InverseLerp(18, 22, self.timeOfDay)
            sunColor = MathUtils.Lerp(full_bright, orange, perc)
        elif self.timeOfDay >= 22 and self.timeOfDay < 24:
            perc = MathUtils.InverseLerp(22, 24, self.timeOfDay)
            sunColor = MathUtils.Lerp(orange, full_dark, perc)
        elif self.timeOfDay >= 0 and self.timeOfDay < 5:
            sunColor = full_dark
        elif self.timeOfDay >= 5 and self.timeOfDay < 7:
            perc = MathUtils.InverseLerp(5, 7, self.timeOfDay)
            sunColor = MathUtils.Lerp(full_dark, orange, perc)
        elif self.timeOfDay >= 7 and self.timeOfDay < 9:
            perc = MathUtils.InverseLerp(7, 9, self.timeOfDay)
            sunColor = MathUtils.Lerp(orange, full_bright, perc)

        self.sun.transform.position = np.array([x,y,z])

        self.sun.color = sunColor


    def run(self):
        """
        Main loop of the scene.

        Calculates delta time, updates the scene and draws it.
        """

        while self.running:
            # handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    LOG("Quitting...", LogLevel.CRITICAL)
                    self.running = False


            fps = self.clock.get_fps()
            dt = 1.0 if fps == 0 else 1.0 / fps

            ms = dt * 1000.0

            pygame.display.set_caption(f"FPS: {fps:.2f} / {ms:.1f}ms")

            self.cameraMovement(dt)
            self.update(dt)

            # MAIN DRAW LOOP
            self.shadow_map()
            self.camera_depth()

            # draw scene with post processing
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.postprocessing.before_draw(self.depthMap, self.sun, self.camera, self.cameraDepthMap)
            glViewport(0, 0, self.width, self.height)

            self.draw_scene(lit_shader)

            grass_field.draw(grass_shader, current_time(), False, self.debugview)
            tree_field.draw(grass_shader, current_time(), False, self.debugview)
            fern_field.draw(grass_shader, current_time(), False, self.debugview)
            water.draw(water_shader, self.camera, current_time(), self.sun)

            self.skybox.draw(skybox_shader, self.camera, self.sun)
            self.postprocessing.after_draw()

            # refreshing
            self.clock.tick(165)
            pygame.display.flip()
    
    def get_mesh(self, name: str) -> Mesh:
        """
        Gets a mesh by its name.

        :param name: The name of the mesh
        :return: The mesh with the given name
        """
        for mesh in self.meshes:
            if mesh.name == name:
                return mesh

        return None

    def cameraMovement(self, dt: float):
        # holding keys
        keys = pygame.key.get_pressed()
        
        # mouse delta
        mouse_delta = pygame.mouse.get_rel()

        # if mouse is held down
        if pygame.mouse.get_pressed()[0]:
            rotX = mouse_delta[0] * dt * 50
            rotY = mouse_delta[1] * dt * 50
            
            self.camera.rotate_local(rotY, rotX)

        speed = 7.0 * dt

        # if holding left shift speed up
        if keys[pygame.K_LSHIFT]:
            speed *= 35

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

    def load_scene(self, path: str):
        """
        Loads a scene from a file.
        
        :param path: The path to the scene file
        """

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

                mat.ambient = material_data["ambient"]
                mat.diffuse = material_data["diffuse"]
                mat.specular = material_data["specular"]
                mat.specularExponent = material_data["specularExponent"]
                mat.metallic = material_data["metallic"]

                if "tiling_speed" in material_data:
                    mat.tiling_speed = material_data["tiling_speed"]

                for tex_name, tex_path in texture_data.items():
                    tex = Texture.Load(tex_path)
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

                if "isIcon" in mesh_data:
                    mesh.isIcon = mesh_data["isIcon"]
                else:
                    mesh.isIcon = False

                if "scripts" in mesh_data:
                    for script in mesh_data["scripts"]:
                        mesh.add_script(script)

                if "one_time_scripts" in mesh_data:
                    scripts = mesh_data["one_time_scripts"]
                    for script in scripts:
                        LOG(f"Running one time script {script} on {mesh_name}", LogLevel.INFO)
                        program = Programs[script]
                        program(mesh)

                self.meshes.append(mesh)
                

def current_time():
    """
    Returns the time since the program started in seconds.
    Used for animations inside shaders.

    :return: The time since the program started in seconds
    """
    return time.time() - start_time


scene = Scene()

# initialize basic shaders
shadow_map_shader = Shader.Shader("shaders/shadow_map/shadow_vertex.glsl", "shaders/shadow_map/shadow_fragment.glsl")
lit_shader = Shader.Shader("shaders/basic/vertex.glsl", "shaders/basic/fragment.glsl")
skybox_shader = Shader.Shader("shaders/skybox/vertex.glsl", "shaders/skybox/fragment.glsl")
postprocess_shader = Shader.Shader("shaders/postprocess/vertex.glsl", "shaders/postprocess/fragment.glsl")
camera_depth_shader = Shader.Shader("shaders/camera/camera_depth_vertex.glsl", "shaders/camera/camera_depth_fragment.glsl")
grass_shader = Shader.Shader("shaders/grass/vertex.glsl", "shaders/grass/fragment.glsl")
shadow_map_trees_shader = Shader.Shader("shaders/grass/vertex.glsl", "shaders/shadow_map/shadow_fragment.glsl")
water_shader = Shader.Shader("shaders/water/vertex.glsl", "shaders/water/fragment.glsl")

scene.postprocessing = PostProcessing(postprocess_shader, scene.width, scene.height)

scene.load_scene("scene.yaml")

# calculated manually inside perlin noise generator for a given seed.
worldYBounds = np.array([-40.0, 22.067507434821415])

grass_field = InstancedField()
grass_field.setup(scene.camera, 
                  scene.sun,
                  worldYBounds,
                  blender.load_mesh("models/jungle/grass_high.obj"),
                  Texture.Load("textures/grass/color.jpg"),
                  Texture.Load("textures/grass/opacity.jpg"),
                  Texture.Load("textures/grass/normal.png"),
                  500_000, 0.5)

grass_field.shadowMap = scene.depthMap

tree_field = InstancedField()
tree_field.setup(scene.camera,
                    scene.sun,
                    worldYBounds,
                    blender.load_mesh("models/jungle/tree_low.obj"),
                    Texture.Load("textures/tree/tree_albedo.png"),
                    None,
                    Texture.Load("textures/tree/tree_normal.png"),
                    25, 0.5)

tree_field.shadowMap = scene.depthMap

fern_field = InstancedField()
fern_field.setup(scene.camera,
                    scene.sun,
                    worldYBounds,
                    blender.load_mesh("models/jungle/fern.obj"),
                    Texture.Load("textures/Fern/color.jpg"),
                    Texture.Load("textures/Fern/opacity.jpg"),
                    Texture.Load("textures/Fern/normal.png"),
                    1_000, 0.5)

fern_field.shadowMap = scene.depthMap

water = Water(np.array([0, -2, 0]), np.array([200,200,200]), scene.skybox)

scene.run()