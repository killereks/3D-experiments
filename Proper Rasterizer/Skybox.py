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
            "textures/cubemap/posx.jpg",
            "textures/cubemap/negx.jpg",
            "textures/cubemap/posy.jpg",
            "textures/cubemap/negy.jpg",
            "textures/cubemap/posz.jpg",
            "textures/cubemap/negz.jpg"
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

    def draw(self, shader, camera):
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubeMap)

        glDepthMask(GL_FALSE)

        glDepthFunc(GL_LEQUAL)
        shader.use()

        proj = camera.getProjectionMatrix()
        view = camera.getViewMatrix()
        view[0][3] = 0
        view[1][3] = 0
        view[2][3] = 0

        glUniformMatrix4fv(shader.get_keyword("view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(shader.get_keyword("projection"), 1, GL_FALSE, proj)
        glUniform1i(shader.get_keyword("skybox"), 1)
        
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glDrawElements(GL_TRIANGLES, len(self.skyboxMesh.faces), GL_UNSIGNED_INT, None)

        glDisableVertexAttribArray(0)

        glDepthFunc(GL_LESS)
        glDepthMask(GL_TRUE)
