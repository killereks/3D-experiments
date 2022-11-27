from Mesh import Mesh
import blender

from OpenGL.GL import *

import numpy as np
import random
from Texture import Texture

import time

class GrassField:
    def setup(self, camera, light):
        self.mesh = blender.load_mesh("models/jungle/grass_blade.obj")
        self.mesh.recalculate_normals()

        glEnableClientState(GL_VERTEX_ARRAY)

        # setup gpu instancing
        self.vbo = glGenBuffers(1)
        self.ibo = glGenBuffers(1)

        # uv data
        self.tbo = glGenBuffers(1)
        # normals
        self.nbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.faces, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.tbo)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.uvs, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.nbo)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.normals, GL_STATIC_DRAW)

        self.albedo = Texture.Load("textures/Grass/color.jpg")
        self.opacity = Texture.Load("textures/Grass/opacity.jpg")

        self.camera = camera
        self.sun = light

    def draw(self, shader, time):
        # both sided drawing
        glDisable(GL_CULL_FACE)

        shader.use()

        glUniformMatrix4fv(shader.get_keyword("projection"), 1, GL_TRUE, self.camera.projectionMatrix)
        glUniformMatrix4fv(shader.get_keyword("view"), 1, GL_TRUE, self.camera.getViewMatrix())
        glUniform1f(shader.get_keyword("time"), time)

        glUniform3fv(shader.get_keyword("sunPos"), 1, self.sun.transform.position)
        glUniform3fv(shader.get_keyword("sunDirection"), 1, -self.sun.transform.position)

        self.albedo.use(0)
        glUniform1i(shader.get_keyword("albedoMap"), 0)

        self.opacity.use(1)
        glUniform1i(shader.get_keyword("opacityMap"), 1)

        #glActiveTexture(GL_TEXTURE0)
        #glBindTexture(GL_TEXTURE_2D, self.heightTexture)
        #glUniform1i(shader.get_keyword("heightMap"), 0)

        # draw the grass and feed vertex data in location 0
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # 1 = uv
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.tbo)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

        # 2 = normals
        glEnableVertexAttribArray(2)
        glBindBuffer(GL_ARRAY_BUFFER, self.nbo)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        # draw grass
        glDrawElementsInstanced(GL_TRIANGLES, len(self.mesh.faces) * 3, GL_UNSIGNED_INT, None, 1_000_000)

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        # enable back face culling
        glEnable(GL_CULL_FACE)


