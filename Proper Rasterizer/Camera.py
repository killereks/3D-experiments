from Transform import Transform
import numpy as np

from custom_logging import LOG

class Camera:
    def __init__(self, fov, near, far):
        self.transform = Transform()
        self.fov = fov
        self.near = near
        self.far = far

        self.aspect = 16 / 9

        self.projectionMatrix = self.getProjectionMatrix()

    def rotate(self, x, y, z):
        self.transform.rotate(x, y, z)

    def getProjectionMatrix(self):
        '''
        Returns a projection matrix for the camera.
        :return: the 4x4 projection matrix
        '''
        fov = np.deg2rad(self.fov)
        
        tan = np.tan(fov / 2)
        
        matrix = np.zeros((4, 4))

        matrix[0][0] = 1 / (tan * self.aspect)
        matrix[1][1] = 1 / tan
        matrix[2][2] = -(self.far + self.near) / (self.far - self.near)
        matrix[2][3] = -1
        matrix[3][2] = -(2 * self.far * self.near) / (self.far - self.near)

        return matrix


    def getViewMatrix(self):
        '''
        Returns a view matrix for the camera.
        :return: the 4x4 view matrix
        '''
        return self.transform.getTRSMatrix()
        