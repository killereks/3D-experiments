import numpy as np

class FaceTypes:
    CULL_BACK = 0
    CULL_FRONT = 1
    DOUBLE_SIDED = 2

class Material:
    def __init__(self, shader):
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
        
        self.textures = []
        self.shader = shader

        self.face_type = FaceTypes.CULL_BACK

    def add_texture(self, tex):
        self.textures.append(tex)

    def use(self):
        for (index, tex) in enumerate(self.textures):
            tex.use(index)
        
        self.shader.use()

    def print(self):
        print(f"Ka: {self.Ka}")
        print(f"Kd: {self.Kd}")
        print(f"Ks: {self.Ks}")
        print(f"Ns: {self.Ns}")
        print(f"Ni: {self.Ni}")
        print(f"d: {self.d}")
        print(f"illum: {self.illum}")