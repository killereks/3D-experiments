from Transform import Transform

from OpenGL.GL import *

from custom_logging import LOG

import numpy as np

import time
import math

class Mesh:
    def __init__(self, vertices, faces, normals, uvs):
        self.vertices = vertices
        self.faces = faces

        self.normals = normals
        self.uvs = uvs

        self.vbo = glGenBuffers(1) #vertex positions
        self.ibo = glGenBuffers(1) #indices

        self.nbo = glGenBuffers(1) #normals
        self.tbo = glGenBuffers(1) #texture coordinates

        self.transform = Transform()

        self.bounds = self.getBoundingBox()

        self.material = None

        self.name = "unnamed"

        LOG(f"Bounds (including scale): {self.bounds * self.transform.scale}")

        self.initialize()

    def set_material(self, material):
        self.material = material

    def getBoundingBox(self):
        min = [0, 0, 0]
        max = [0, 0, 0]

        for i in range(len(self.vertices)):
            for j in range(len(self.vertices[i])):
                if self.vertices[i][j] < min[j]:
                    min[j] = self.vertices[i][j]
                if self.vertices[i][j] > max[j]:
                    max[j] = self.vertices[i][j]

        return [min, max]

    def recalculate_normals(self):
        self.normals = np.zeros(self.vertices.shape, dtype="f")
        
        for f in range(self.faces.shape[0]):
            a = self.vertices[self.faces[f, 1]] - self.vertices[self.faces[f, 0]]
            b = self.vertices[self.faces[f, 2]] - self.vertices[self.faces[f, 0]]
            n = np.cross(a, b)

            for j in range(3):
                self.normals[self.faces[f,j],:] += n

        self.normals /= np.linalg.norm(self.normals, axis=1, keepdims=True)

        LOG(f"Recalculated normals for mesh {self} with {len(self.normals)} normals")

        self.initialize()

    def initialize(self):
        glEnableClientState(GL_VERTEX_ARRAY)

        # vertex positions
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices, GL_STATIC_DRAW)

        # indices (faces)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces, GL_STATIC_DRAW)

        # normals
        glBindBuffer(GL_ARRAY_BUFFER, self.nbo)
        glBufferData(GL_ARRAY_BUFFER, self.normals, GL_STATIC_DRAW)

        # texture coordinates (UVs)
        glBindBuffer(GL_ARRAY_BUFFER, self.tbo)
        glBufferData(GL_ARRAY_BUFFER, self.uvs, GL_STATIC_DRAW)

    def draw(self):
        glEnableClientState(GL_VERTEX_ARRAY)

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.nbo)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(2)
        glBindBuffer(GL_ARRAY_BUFFER, self.tbo)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)

        # feed buffer data into attribute variables

        """glEnableVertexAttribArray(0)
        glVertexAttribPointer(index=0, size=self.vertices.shape[1], type=GL_FLOAT, normalized=False, stride=0, pointer=None)

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(index=1, size=self.normals.shape[1], type=GL_FLOAT, normalized=False, stride=0, pointer=None)

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(index=2, size=self.uvs.shape[1], type=GL_FLOAT, normalized=False, stride=0, pointer=None)"""

        glDrawElements(GL_TRIANGLES, self.faces.size, GL_UNSIGNED_INT, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)


    def update(self, dt):
        pass
        #self.transform.rotateAxis([0, 1, 0], dt * 5)