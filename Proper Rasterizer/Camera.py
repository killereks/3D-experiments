from Transform import Transform
import numpy as np

from custom_logging import LOG

class Camera:
    def __init__(self, fov, aspect, near, far):
        self.transform = Transform()
        self.fov = fov
        self.near = near
        self.far = far

        self.aspect = aspect

        self.projectionMatrix = self.getProjectionMatrix()

    def rotate(self, x, y, z):
        self.transform.rotate(x, y, z)

    def getProjectionMatrix(self):
        '''
        Returns a projection matrix for the camera.
        :return: the 4x4 projection matrix
        '''
        
        fov_r = np.deg2rad(self.fov)
        aspect = self.aspect

        tan = np.tan(fov_r * 0.5)

        far = self.far
        near = self.near

        return np.array([
            [1 / (aspect * tan), 0, 0, 0],
            [0, 1/tan, 0, 0],
            [0, 0, -(far + near) / (far - near), -(2 * far * near) / (far - near)],
            [0, 0, -1, 0]
        ])



    def getViewMatrix(self):
        '''
        Returns a view matrix for the camera.
        :return: the 4x4 view matrix
        '''
        R = self.transform.rotation.ToMatrix()
        T = self.transform.getTranslationMatrix()
        return np.matmul(R, T)
        