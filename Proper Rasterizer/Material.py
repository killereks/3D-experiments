import numpy as np
from OpenGL.GL import *

from Texture import Texture
from Shader import Shader

class FaceTypes:
    CULL_BACK = 0
    CULL_FRONT = 1
    DOUBLE_SIDED = 2

class Material:
    def __init__(self):
        # ambient
        self.Ka = 0.2
        # diffuse
        self.Kd = 0.8
        # specular
        self.Ks = 1
        # specular exponent
        self.Ns = 10.0
        # metallic
        self.metallic = 0.0
        
        self.textures = {}

        self.face_type = FaceTypes.CULL_BACK

        self.tiling = np.array([1,1])
        self.tiling_speed = np.array([0,0],"f")

        self.name = "default"

        self.shader = None

    def add_texture(self, tex: Texture, name: str):
        """
        Add a texture to the material
        
        :param tex: the texture to add
        :param name: the name of the texture, used in the shader
        """
        self.textures[name] = tex

    def use(self, shader: Shader):
        """
        Use the material in the shader
        
        :param shader: the shader to use for this material
        """
        shader.use()

        # enumerate over all the textures, with index and name
        for index, name in enumerate(self.textures):
            texture = self.textures[name]
            texture.use(index+1) # 0 = shadow map
            glUniform1i(shader.get_keyword(name), index+1)

        # material uniforms
        glUniform2fv(shader.get_keyword("tiling"), 1, self.tiling)
        glUniform2fv(shader.get_keyword("tiling_speed"), 1, np.array(self.tiling_speed, "f"))

        glUniform1f(shader.get_keyword("Ka"), self.Ka)
        glUniform1f(shader.get_keyword("Kd"), self.Kd)
        glUniform1f(shader.get_keyword("Ks"), self.Ks)
        
        glUniform1f(shader.get_keyword("Ns"), self.Ns)
        glUniform1f(shader.get_keyword("metallic"), self.metallic)
        

    def print(self):
        print(f"Ka: {self.Ka}")
        print(f"Kd: {self.Kd}")
        print(f"Ks: {self.Ks}")
        print(f"Ns: {self.Ns}")
        print(f"Ni: {self.Ni}")
        print(f"d: {self.d}")
        print(f"illum: {self.illum}")