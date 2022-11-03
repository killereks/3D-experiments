from OpenGL.GL import *

import blender

import pygame

from Camera import Camera

class Skybox:
    def __init__(self):
        self.cubeMap = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubeMap)

        self.skyboxMesh = blender.load_mesh("models/skybox.obj")

        file_paths = [
            "textures/cubemap/negx.jpg",
            "textures/cubemap/posx.jpg",
            "textures/cubemap/negy.jpg",
            "textures/cubemap/posy.jpg",
            "textures/cubemap/negz.jpg",
            "textures/cubemap/posz.jpg"
        ]

        for index, file_path in enumerate(file_paths):
            image = pygame.image.load(file_path).convert()
            image_width, image_height = image.get_rect().size
            img_data = pygame.image.tostring(image, 'RGBA')
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + index, 0, GL_RGB, image_width, image_height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubeMap)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.skyboxMesh.vertices, GL_STATIC_DRAW)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.skyboxMesh.faces, GL_STATIC_DRAW)

    def draw(self, shader, camera):
        glDepthFunc(GL_LEQUAL)
        shader.use()
        
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubeMap)
        
        glUniform1i(shader.get_keyword("skybox"), 0)

        view = camera.getViewMatrix()
        view[3][0] = 0
        view[3][1] = 0
        view[3][2] = 0
        glUniformMatrix4fv(shader.get_keyword("view"), 1, GL_TRUE, view)

        projection = camera.getProjectionMatrix()
        glUniformMatrix4fv(shader.get_keyword("projection"), 1, GL_TRUE, projection)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawElements(GL_TRIANGLES, len(self.skyboxMesh.faces) * 3, GL_UNSIGNED_INT, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        glDisableVertexAttribArray(0)
        glDepthFunc(GL_LESS)
