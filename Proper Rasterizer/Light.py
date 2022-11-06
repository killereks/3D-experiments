from Transform import Transform
from Camera import Camera

import numpy as np

class Light:
    def __init__(self, color: list, intensity: float):
        self.color = color
        self.intensity = intensity
        self.transform = Transform()

    def getDirection(self):
        """
        :return: the direction of the light in world space
        """
        return self.transform.forward()

    def getLightProjection(self):
        """
        Projection matrix for the light.
        
        It needs to be big enough to cover the entire scene, but enough for shadows to be crisp.

        :return: the projection matrix for the light
        """
        size = 15
        return Camera.getOrthographicMatrix(-size, size, -size, size, 0.1, 30)

    def getLightView(self):
        """
        :return: the view matrix for the light
        """
        return Camera.lookAt(self.transform.position, np.array([0,0,0]), np.array([0,1,0]))

    def getLightSpaceMatrix(self):
        """
        :return: the light space matrix
        """
        return np.matmul(self.getLightProjection(), self.getLightView())