import numpy as np
from OpenGL.GL import *

class FaceTypes:
    CULL_BACK = 0
    CULL_FRONT = 1
    DOUBLE_SIDED = 2

class Material:
    def __init__(self):
        # ambient
        self.Ka = np.array([0.2, 0.2, 0.2])
        # diffuse
        self.Kd = np.array([0.8, 0.8, 0.8])
        # specular
        self.Ks = np.array([1.0, 1.0, 1.0])
        # specular exponent
        self.Ns = 0.0
        # optical density
        self.Ni = 1.0
        # dissolve
        self.d = 1.0
        # illumination
        self.illum = 2
        
        self.textures = {}

        self.face_type = FaceTypes.CULL_BACK

        self.tiling = np.array([1,1])

        self.name = "default"

    def add_texture(self, tex, name):
        self.textures[name] = tex

    def use(self, shader):
        shader.use()

        # enumerate over all the textures, with index and name
        for index, name in enumerate(self.textures):
            texture = self.textures[name]
            texture.use(index+1) # 0 = shadow map so we start at 1
            glUniform1i(shader.get_keyword(name), 1)

        # material uniforms
        glUniform2fv(shader.get_keyword("tiling"), 1, self.tiling)
        

    def print(self):
        print(f"Ka: {self.Ka}")
        print(f"Kd: {self.Kd}")
        print(f"Ks: {self.Ks}")
        print(f"Ns: {self.Ns}")
        print(f"Ni: {self.Ni}")
        print(f"d: {self.d}")
        print(f"illum: {self.illum}")