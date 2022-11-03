from Transform import Transform
from Camera import Camera

import numpy as np

class Light:
    def __init__(self, color, intensity):
        self.color = color
        self.intensity = intensity
        self.transform = Transform()

    def getDirection(self):
        return self.transform.forward()

    def getLightProjection(self):
        size = 50
        return Camera.getOrthographicMatrix(-size, size, -size, size, 0.1, 30)

    def getLightView(self):
        return Camera.lookAt(self.transform.position, np.array([0,0,0]), np.array([0,1,0]))

    def getLightSpaceMatrix(self):
        return np.matmul(self.getLightProjection(), self.getLightView())