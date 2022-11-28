from Transform import Transform

from OpenGL.GL import *

from custom_logging import LOG

import numpy as np

import Material

from Programs import Programs

class Mesh:
    def __init__(self, vertices: np.ndarray, faces: np.ndarray, normals: np.ndarray, uvs: np.ndarray):
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

        LOG(f"Bounds (including scale): {self.bounds[0] * self.transform.scale} - {self.bounds[1] * self.transform.scale}")

        self.isIcon = False

        self.scripts = []

        self.initialize()

    def add_script(self, script):
        """
        Adds a script to the mesh
        
        :param script: The script to add
        """
        program = Programs[script]
        self.scripts.append(program)

    def set_material(self, material: Material):
        """
        Sets the material of the mesh
        
        :param material: The material to set
        """
        self.material = material

    def getBoundingBox(self):
        """
        Returns the bounding box of the mesh, i.e. smallest box that contains the mesh
        
        :return: The bounding box of the mesh"""
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
        """
        Recalculates the normals of the mesh and updates the VBO
        """
        self.normals = np.zeros(self.vertices.shape, dtype="f")
        
        for f in range(self.faces.shape[0]):
            a = self.vertices[self.faces[f, 1]] - self.vertices[self.faces[f, 0]]
            b = self.vertices[self.faces[f, 2]] - self.vertices[self.faces[f, 0]]
            n = np.cross(a, b)

            for j in range(3):
                self.normals[self.faces[f,j],:] += n

        self.normals /= np.linalg.norm(self.normals, axis=1, keepdims=True)

        LOG(f"Recalculated normals for mesh {self.name} with {len(self.normals)} normals")

        self.initialize()

    def initialize(self):
        """
        Initializes the mesh, i.e. uploads the data to the GPU
        """
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
        """
        Draws the mesh using the currently bound shader
        """
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

        glDrawElements(GL_TRIANGLES, self.faces.size, GL_UNSIGNED_INT, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)


    def update(self, dt: float):
        """
        Updates the mesh position, rotation and scale
        """
        for script in self.scripts:
            script(self, dt)

    @staticmethod
    def CreateScreenQuad():
        """
        Creates a quad mesh that fills the entire screen
        """
        vertices = np.array([
            [-1, -1, 0],
            [1, -1, 0],
            [1, 1, 0],
            [-1, 1, 0]
        ], dtype="f")

        faces = np.array([
            [0, 1, 2],
            [0, 2, 3]
        ], dtype="i")

        normals = np.array([
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]
        ], dtype="f")
        
        uvs = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1]
        ], dtype="f")

        mesh = Mesh(vertices, faces, normals, uvs)
        mesh.name = "ScreenQuad"

        return mesh

    @staticmethod
    def CreateQuad(divisions):
        """
        Creates a quad mesh with the given number of divisions
        
        :param divisions: The number of divisions
        :return: The quad mesh
        """
        vertices = []
        faces = []
        normals = []
        uvs = []

        for i in range(divisions + 1):
            for j in range(divisions + 1):
                vertices.append([i / divisions, j / divisions, 0])
                normals.append([0, 0, 1])
                uvs.append([i / divisions, j / divisions])

        for i in range(divisions):
            for j in range(divisions):
                faces.append([i * (divisions + 1) + j, i * (divisions + 1) + j + 1, (i + 1) * (divisions + 1) + j + 1])
                faces.append([i * (divisions + 1) + j, (i + 1) * (divisions + 1) + j + 1, (i + 1) * (divisions + 1) + j])

        vertices = np.array(vertices, dtype="f")
        faces = np.array(faces, dtype="i")
        normals = np.array(normals, dtype="f")
        uvs = np.array(uvs, dtype="f")

        mesh = Mesh(vertices, faces, normals, uvs)
        mesh.name = "Quad"

        return mesh

        
        