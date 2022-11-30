from Transform import Transform

from OpenGL.GL import *

import blender
from Shader import Shader
from Camera import Camera
from Light import Light
from Texture import Texture

class Water:
    def __init__(self, position, scale, skybox):
        self.transform = Transform()
        self.transform.position = position
        self.transform.scale = scale

        self.vbo = glGenBuffers(1) #vertex positions
        self.ibo = glGenBuffers(1) #indices
        self.uvo = glGenBuffers(1) #uv coordinates

        self.mesh = blender.load_mesh("models/jungle/divided_quad.obj")

        self.texture = Texture.Load("textures/Ground/color.jpg")

        self.heightMap = Texture.Load("textures/heightmap.png")

        self.skybox = skybox

        self.initialize()


    def initialize(self):
        """
        Initializes the water
        """
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.uvo)
        glBufferData(GL_ARRAY_BUFFER, self.mesh.uvs, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.faces, GL_STATIC_DRAW)

    def draw(self, shader: Shader, camera: Camera, time: float, sun: Light):
        """
        Draws the water
        """
        shader.use()

        # activate transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.texture.use(0)
        glUniform1i(shader.get_keyword("albedo"), 0)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.skybox.cubeMap)
        glUniform1i(shader.get_keyword("_Skybox"), 1)

        self.heightMap.use(2)
        glUniform1i(shader.get_keyword("heightMap"), 2)

        glUniformMatrix4fv(shader.get_keyword("model"), 1, GL_TRUE, self.transform.getTRSMatrix())
        glUniformMatrix4fv(shader.get_keyword("view"), 1, GL_TRUE, camera.getViewMatrix())
        glUniformMatrix4fv(shader.get_keyword("projection"), 1, GL_TRUE, camera.projectionMatrix)

        glUniform1f(shader.get_keyword("time"), time)

        glUniform3fv(shader.get_keyword("sunPos"), 1, sun.transform.position)
        glUniform3fv(shader.get_keyword("sunDir"), 1, -sun.transform.position)

        glUniform3fv(shader.get_keyword("camPos"), 1, camera.transform.position)
        glUniform3fv(shader.get_keyword("camFwd"), 1, camera.forward())


        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.uvo)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        glDrawElements(GL_TRIANGLES, len(self.mesh.faces) * 3, GL_UNSIGNED_INT, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)

        glDisable(GL_BLEND)
        