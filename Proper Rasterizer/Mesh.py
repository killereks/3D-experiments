from Transform import Transform

from OpenGL.GL import *

from custom_logging import LOG

import time
import math

class Mesh:
    def __init__(self, vertices, faces, normals, uvs):
        self.vertices = vertices
        self.faces = faces

        self.normals = normals
        self.uvs = uvs

        self.vbo = glGenBuffers(1)
        self.ibo = glGenBuffers(1)

        self.transform = Transform()

        self.bounds = self.getBoundingBox()

        self.transform.scaleMult(0.3, 0.3, 0.3)

        LOG(f"Bounds: {self.bounds}")

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

    def draw(self):
        self.transform.rotateAxis([0, 1, 0], 1)

        glEnableClientState(GL_VERTEX_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces, GL_STATIC_DRAW)

        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawElements(GL_TRIANGLES, len(self.faces) * 3, GL_UNSIGNED_INT, None)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(index=0, size=self.vertices.shape[1], type=GL_FLOAT, normalized=False, stride=0, pointer=None)

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(index=1, size=self.normals.shape[1], type=GL_FLOAT, normalized=False, stride=0, pointer=None)

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(index=2, size=self.uvs.shape[1], type=GL_FLOAT, normalized=False, stride=0, pointer=None)