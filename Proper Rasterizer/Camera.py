from Transform import Transform
import numpy as np

from Shader import Shader

from custom_logging import LOG

from OpenGL.GL import *

class Camera:
    def __init__(self, fov: float, aspect: float, near: float, far: float):
        self.transform = Transform()
        self.fov = fov
        self.near = near
        self.far = far

        self.aspect = aspect

        self.projectionMatrix = self.getProjectionMatrix()

        self.rotX = 0
        self.rotY = 0

    def rotate_local(self, x: float, y: float):
        """
        Rotates the camera by the given amount.

        We don't want to use Quaternions here because we want to rotate the camera around the local axes.

        :param x: the amount to rotate on the x axis
        :param y: the amount to rotate on the y axis
        """
        self.rotX += x
        self.rotY += y

        # clamp rotX to -90 and 90
        self.rotX = np.min([np.max([self.rotX, -90]), 90])


    def getProjectionMatrix(self):
        '''
        Calculates the projection matrix for the camera.
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
    def getOrthographicMatrix(left: float, right: float, bottom: float, top: float, near: float, far: float):
        """
        Returns an orthographic projection matrix.
        :param left: the left plane
        :param right: the right plane
        :param bottom: the bottom plane
        :param top: the top plane
        :param near: the near plane
        :param far: the far plane
        """

        return np.array([
            [2 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -2 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1]
        ])

    def forward(self):
        """
        Returns the forward vector of the camera.
        
        :return: the forward vector
        """
        rx = np.deg2rad(self.rotX)
        ry = -np.deg2rad(self.rotY)
        rz = np.deg2rad(0)
        
        x = np.sin(ry)
        y = np.sin(rx)
        z = np.cos(ry)

        return np.array([x, y, z])
        #return Quaternion.MultiplyVector(Quaternion.FromEuler(-self.rotX, -self.rotY, 0), np.array([0,0,1]))

    def right(self):
        """
        Returns the right vector of the camera.

        :return: the right vector
        """
        rx = np.deg2rad(self.rotX)
        ry = -np.deg2rad(self.rotY)
        rz = np.deg2rad(0)

        x = np.cos(ry)
        y = 0
        z = -np.sin(ry)

        return np.array([x, y, z])

        #return Quaternion.MultiplyVector(Quaternion.FromEuler(-self.rotX, -self.rotY, 0), np.array([1,0,0]))

    def up(self):
        """
        Returns the up vector of the camera.

        :return: the up vector
        """

        rx = -np.deg2rad(self.rotX)
        ry = -np.deg2rad(self.rotY)
        rz = np.deg2rad(0)

        x = np.sin(ry) * np.sin(rx)
        y = np.cos(-rx)
        z = np.cos(ry) * np.sin(rx)

        return np.array([x, y, z])

        #return Quaternion.MultiplyVector(Quaternion.FromEuler(-self.rotX, -self.rotY, 0), np.array([0,1,0]))


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
        
        :param pos: the position of the camera
        :param target: the target of the camera (where it's looking)
        :param up: the up vector of the camera (usually [0,1,0])

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
        