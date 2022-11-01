import math
import numpy as np

from Quaternion import Quaternion

class Transform:
    def __init__(self):
        self.position = np.array([0., 0., 0.])
        self.rotation = Quaternion.identity()
        self.scale = np.array([1., 1., 1.])

    def translate(self, x, y, z):
        self.position += np.array([x, y, z])

    def rotate(self, x, y, z):
        self.rotation *= Quaternion.FromEuler(x, y, z)

    def scaleAdd(self, x, y, z):
        self.scale += np.array([x, y, z])
    
    def scaleMult(self, x, y, z):
        self.scale *= np.array([x, y, z])
    
    def getTRSMatrix(self):
        '''
        Returns a combined TRS matrix for the pose of a model.
        :return: the 4x4 TRS matrix
        '''

        # M=TRS

        T = self.getTranslationMatrix()
        R = self.rotation.ToMatrix()
        S = self.getScaleMatrix()
        
        return np.matmul(T, np.matmul(R, S))

    def forward(self):
        # multiply rotation matrix by (0,0,1) to get forward vector
        return Quaternion.MultiplyVector(self.rotation, np.array([0,0,1]))
    
    def up(self):
        # multiply rotation matrix by (0,1,0) to get up vector
        return Quaternion.MultiplyVector(self.rotation, np.array([0,1,0]))
        
    
    def right(self):
        # multiply rotation matrix by (1,0,0) to get right vector
        return Quaternion.MultiplyVector(self.rotation, np.array([1,0,0]))

    def getTranslationMatrix(self):
        matrix = np.identity(4)
        matrix[0][3] = self.position[0]
        matrix[1][3] = self.position[1]
        matrix[2][3] = self.position[2]
        return matrix

    def getScaleMatrix(self):
        matrix = np.identity(4)
        matrix[0][0] = self.scale[0]
        matrix[1][1] = self.scale[1]
        matrix[2][2] = self.scale[2]
        return matrix

    def rotateAxis(self, vector, angle):
        self.rotation *= Quaternion.FromAxisAngle(vector, angle)