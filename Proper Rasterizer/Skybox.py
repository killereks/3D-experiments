from OpenGL.GL import *

import blender

import pygame

from Camera import Camera
from Shader import Shader
from Light import Light

import numpy as np

class Skybox:
    def __init__(self):
        self.cubeMap = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubeMap)

        self.skyboxMesh = blender.load_mesh("models/skybox.obj")

        file_paths = [
            "textures/cubemap/islands/right.jpg",
            "textures/cubemap/islands/left.jpg",
            "textures/cubemap/islands/top.jpg",
            "textures/cubemap/islands/bottom.jpg",
            "textures/cubemap/islands/front.jpg",
            "textures/cubemap/islands/back.jpg"
        ]

        for index, file_path in enumerate(file_paths):
            image = pygame.image.load(file_path).convert()
            image_width, image_height = image.get_rect().size
            img_data = pygame.image.tostring(image, 'RGB')
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + index, 0, GL_RGB, image_width, image_height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubeMap)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glBufferData(GL_ARRAY_BUFFER, self.skyboxMesh.vertices, GL_STATIC_DRAW)

        self.ibo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.skyboxMesh.faces, GL_STATIC_DRAW)

    def draw(self, shader: Shader, camera: Camera, sun: Light):
        """
        Draws the skybox
        
        :param shader: The shader to use, must be a skybox shader
        :param camera: The camera to use, to get the view and projection matrices
        """

        glDepthMask(GL_FALSE)

        glDisable(GL_CULL_FACE)

        glDepthFunc(GL_LEQUAL)
        shader.use()

        proj = camera.getProjectionMatrix()
        view = camera.getViewMatrix()
        view[0][3] = 0
        view[1][3] = 0
        view[2][3] = 0

        glUniformMatrix4fv(shader.get_keyword("view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(shader.get_keyword("projection"), 1, GL_TRUE, proj)
        glUniform1i(shader.get_keyword("skybox"), 1)

        glUniform3fv(shader.get_keyword("sunColor"), 1, sun.color)
        
        glBindVertexArray(self.vao)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubeMap)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        
        glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)
        
        glDisableVertexAttribArray(0)
        glBindVertexArray(0)

        glDepthFunc(GL_LESS)
        glDepthMask(GL_TRUE)

        glEnable(GL_CULL_FACE)
