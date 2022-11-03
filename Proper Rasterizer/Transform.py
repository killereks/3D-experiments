import math
import numpy as np

from Quaternion import Quaternion

class Transform:
    def __init__(self):
        self.position = np.array([0., 0., 0.],"f")
        self.rotation = Quaternion.identity()
        self.scale = np.array([1., 1., 1.])

    def translate(self, x, y, z):
        self.position += np.array([x, y, z])

    def rotate(self, x, y, z):
        self.rotation *= Quaternion.FromEuler(x, y, z)

    def rotateLocal(self, x, y, z):
        self.rotateAxis(self.right(), x)
        self.rotateAxis(self.up(), y)
        self.rotateAxis(self.forward(), z)

    def scaleAdd(self, x, y, z):
        self.scale += np.array([x, y, z])

    def scaleAllMult(self, scale):
        self.scale *= scale
    
    def scaleMult(self, x, y, z):
        self.scale *= np.array([x, y, z])
    
    def getTRSMatrix(self):
        '''
        Returns a combined TRS matrix for the pose of a model.
        :return: the 4x4 TRS matrix
        '''

        # SCALE then ROTATE then TRANSLATE

        # M=TRS

        T = self.getTranslationMatrix()
        R = self.rotation.ToMatrix()
        S = self.getScaleMatrix()
        
        return np.matmul(T, np.matmul(R, S))

    def forward(self):
        return Quaternion.MultiplyVector(self.rotation, np.array([0,0,1]))
    
    def right(self):
        return Quaternion.MultiplyVector(self.rotation, np.array([1,0,0]))

    def up(self):
        return Quaternion.MultiplyVector(self.rotation, np.array([0,1,0]))

        
    """def forward(self):
        rotX, rotY, rotZ = self.rotation.ToEuler()

        rotX = np.radians(rotX)
        rotY = np.radians(rotY)
        rotZ = np.radians(rotZ)
        
        x = np.sin(rotY) * np.cos(rotX)
        y = np.sin(-rotX)
        z = np.cos(rotX) * np.cos(rotY)

        return np.array([x, y, z])

    def right(self):
        rotX, rotY, rotZ = self.rotation.ToEuler()

        rotX = np.radians(rotX)
        rotY = np.radians(rotY)
        rotZ = np.radians(rotZ)

        x = np.cos(rotY)
        y = 0
        z = -np.sin(rotY)

        return np.array([x, y, z])

    def up(self):
        return np.cross(self.forward(), self.right())"""
            

    def getTranslationMatrix(self):
        return np.array([
            [1, 0, 0, self.position[0]],
            [0, 1, 0, self.position[1]],
            [0, 0, 1, self.position[2]],
            [0, 0, 0, 1]
        ],"f")

    def getScaleMatrix(self):
        return np.array([
            [self.scale[0], 0, 0, 0],
            [0, self.scale[1], 0, 0],
            [0, 0, self.scale[2], 0],
            [0, 0, 0, 1]
        ],"f")

    def rotateAxis(self, vector, angle):
        self.rotation *= Quaternion.FromAxisAngle(vector, angle)

    @staticmethod
    def lookAt(position, target, up):
        zaxis = np.subtract(position, target)
        zaxis = zaxis / np.linalg.norm(zaxis)

        xaxis = np.cross(up, zaxis)
        xaxis = xaxis / np.linalg.norm(xaxis)

        yaxis = np.cross(zaxis, xaxis)
        yaxis = yaxis / np.linalg.norm(yaxis)

        return np.array([
            [xaxis[0], yaxis[0], zaxis[0], position[0]],
            [xaxis[1], yaxis[1], zaxis[1], position[1]],
            [xaxis[2], yaxis[2], zaxis[2], position[2]],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def RotationMatrixX(angle):
        angle = np.radians(angle)

        return np.array([
            [1, 0, 0, 0],
            [0, np.cos(angle), -np.sin(angle), 0],
            [0, np.sin(angle), np.cos(angle), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def RotationMatrixY(angle):
        angle = np.radians(angle)

        return np.array([
            [np.cos(angle), 0, np.sin(angle), 0],
            [0, 1, 0, 0],
            [-np.sin(angle), 0, np.cos(angle), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def RotationMatrixZ(angle):
        angle = np.radians(angle)

        return np.array([
            [np.cos(angle), -np.sin(angle), 0, 0],
            [np.sin(angle), np.cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])