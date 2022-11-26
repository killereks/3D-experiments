import math
import numpy as np

from Quaternion import Quaternion

class Transform:
    def __init__(self):
        self.position = np.array([0., 0., 0.],"f")
        self.rotation = Quaternion.identity()
        self.scale = np.array([1., 1., 1.])

    def translate(self, x: float, y: float, z: float):
        """
        Translates the transform by the given amount.
        """
        self.position += np.array([x, y, z])

    def rotate(self, x: float, y: float, z: float):
        """
        Rotates the transform by the given amount, in local space.
        """
        self.rotation *= Quaternion.FromEuler(x, y, z)

    def scaleAdd(self, x: float, y: float, z: float):
        """
        Scales the transform by the given amount additively.
        """
        self.scale += np.array([x, y, z])

    def scaleAllMult(self, scale: float):
        """
        Scales each axis by the given amount multiplicatively.
        """
        self.scale *= scale
    
    def scaleMult(self, x: float, y: float, z: float):
        """
        Scales each axis separately by the given amount multiplicatively.
        """
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
        """
        :return: the forward vector
        """
        return Quaternion.MultiplyVector(self.rotation, np.array([0,0,1]))
    
    def right(self):
        """
        :return: the right vector
        """
        return Quaternion.MultiplyVector(self.rotation, np.array([1,0,0]))

    def up(self):
        """
        :return: the up vector
        """
        return Quaternion.MultiplyVector(self.rotation, np.array([0,1,0]))
            

    def getTranslationMatrix(self):
        """
        :return: the 4x4 translation matrix
        """
        return np.array([
            [1, 0, 0, self.position[0]],
            [0, 1, 0, self.position[1]],
            [0, 0, 1, self.position[2]],
            [0, 0, 0, 1]
        ],"f")

    def getScaleMatrix(self):
        """
        :return: the 4x4 scale matrix
        """
        return np.array([
            [self.scale[0], 0, 0, 0],
            [0, self.scale[1], 0, 0],
            [0, 0, self.scale[2], 0],
            [0, 0, 0, 1]
        ],"f")

    def rotateAxis(self, vector: np.ndarray, angle: float):
        """
        Rotates the transform by the given amount, in local space, around the given axis.

        :param vector: the axis to rotate around
        :param angle: the angle to rotate by in degrees
        """
        self.rotation *= Quaternion.FromAxisAngle(vector, angle)

    def lookAtSelf(self, target: np.ndarray, up: np.ndarray):
        """
        Sets the rotation of the transform to look at the given target, with the given up vector.
        
        :param target: the target look at point
        :param up: the up vector (usually [0,1,0])"""
        
        position = self.position
        
        zaxis = np.subtract(position, target)
        zaxis = zaxis / np.linalg.norm(zaxis)

        xaxis = np.cross(up, zaxis)
        xaxis = xaxis / np.linalg.norm(xaxis)

        yaxis = np.cross(zaxis, xaxis)
        yaxis = yaxis / np.linalg.norm(yaxis)

        self.rotation = Quaternion.FromMatrix(np.array([
            [xaxis[0], yaxis[0], zaxis[0]],
            [xaxis[1], yaxis[1], zaxis[1]],
            [xaxis[2], yaxis[2], zaxis[2]]
        ]))
        

    @staticmethod
    def RotationMatrixX(angle: float):
        """
        Creates a rotation matrix for the given angle around the X axis.
        
        :param angle: the angle to rotate by in degrees
        :return: the 4x4 rotation matrix
        """

        angle = np.radians(angle)

        return np.array([
            [1, 0, 0, 0],
            [0, np.cos(angle), -np.sin(angle), 0],
            [0, np.sin(angle), np.cos(angle), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def RotationMatrixY(angle: float):
        """
        Creates a rotation matrix for the given angle around the Y axis.

        :param angle: the angle to rotate by in degrees
        :return: the 4x4 rotation matrix
        """

        angle = np.radians(angle)

        return np.array([
            [np.cos(angle), 0, np.sin(angle), 0],
            [0, 1, 0, 0],
            [-np.sin(angle), 0, np.cos(angle), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def RotationMatrixZ(angle: float):
        """
        Creates a rotation matrix for the given angle around the Z axis.

        :param angle: the angle to rotate by in degrees
        :return: the 4x4 rotation matrix
        """
        angle = np.radians(angle)

        return np.array([
            [np.cos(angle), -np.sin(angle), 0, 0],
            [np.sin(angle), np.cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])