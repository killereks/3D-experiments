from Transform import Transform
import numpy as np

from custom_logging import LOG

from Quaternion import Quaternion

class Camera:
    def __init__(self, fov, aspect, near, far):
        self.transform = Transform()
        self.fov = fov
        self.near = near
        self.far = far

        self.aspect = aspect

        self.projectionMatrix = self.getProjectionMatrix()

        self.rotX = 0
        self.rotY = 0

    def rotate_local(self, x, y):
        self.rotX += x
        self.rotY += y

        # clamp rotX to -89 to 89 degrees
        self.rotX = np.min([np.max([self.rotX, -89]), 89])


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

    @staticmethod
    def getOrthographicMatrix(left, right, bottom, top, near, far):
        return np.array([
            [2 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -2 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1]
        ])

    def forward(self):
        return Quaternion.MultiplyVector(Quaternion.FromEuler(-self.rotX, -self.rotY, 0), np.array([0,0,1]))

    def right(self):
        return Quaternion.MultiplyVector(Quaternion.FromEuler(-self.rotX, -self.rotY, 0), np.array([1,0,0]))

    def up(self):
        return Quaternion.MultiplyVector(Quaternion.FromEuler(-self.rotX, -self.rotY, 0), np.array([0,1,0]))


    def getViewMatrix(self):
        '''
        Returns a view matrix for the camera.
        :return: the 4x4 view matrix
        '''
        #R = self.transform.rotation.ToMatrix()
        T = self.transform.getTranslationMatrix()

        R_X = Transform.RotationMatrixX(self.rotX)
        R_Y = Transform.RotationMatrixY(self.rotY)

        R = np.matmul(R_X, R_Y)

        return np.matmul(R, T)

    @staticmethod
    def lookAt(pos, target, up):
        '''
        Returns a view matrix for the camera.
        :return: the 4x4 view matrix
        '''
        
        # forward
        f = np.subtract(target, pos)
        f = f / np.linalg.norm(f)

        # right
        r = np.cross(f, up)
        r = r / np.linalg.norm(r)

        # up
        u = np.cross(r, f)

        return np.array([
            [r[0], r[1], r[2], -np.dot(r, pos)],
            [u[0], u[1], u[2], -np.dot(u, pos)],
            [-f[0], -f[1], -f[2], np.dot(f, pos)],
            [0, 0, 0, 1]
        ])
        