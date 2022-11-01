import unittest

import numpy as np

#import from parent directory
import sys
sys.path.insert(1, '..')

from Quaternion import Quaternion

class QuaternionTests(unittest.TestCase):
    def test_Quaternion_ToMatrix(self):
        q = Quaternion(0.5, 0.5, 0.5, 0.5)
        m = q.ToMatrix()
        expected = np.array([
            [0.0, 0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
        self.assertTrue(np.allclose(m, expected))

    def test_Quaternion_ToEuler(self):
        q = Quaternion(0.5, 0.5, 0.5, 0.5)
        e = q.ToEuler()
        expected = np.array([45.0, 45.0, 45.0])
        self.assertTrue(np.allclose(e, expected))

    def test_Quaternion_Inverse(self):
        q = Quaternion(0.5, 0.5, 0.5, 0.5)
        q_inv = Quaternion.Inverse(q)
        expected = Quaternion(0.5, -0.5, -0.5, -0.5)
        self.assertTrue(np.allclose(q_inv.w, expected.w))
        self.assertTrue(np.allclose(q_inv.x, expected.x))
        self.assertTrue(np.allclose(q_inv.y, expected.y))
        self.assertTrue(np.allclose(q_inv.z, expected.z))

    def test_Quaternion_Multiply(self):
        q1 = Quaternion(0.5, 0.5, 0.5, 0.5)
        q2 = Quaternion(0.5, 0.5, 0.5, 0.5)
        q3 = q1 * q2
        expected = Quaternion(0.5, 0.5, 0.5, 0.5)
        self.assertTrue(np.allclose(q3.w, expected.w))
        self.assertTrue(np.allclose(q3.x, expected.x))
        self.assertTrue(np.allclose(q3.y, expected.y))
        self.assertTrue(np.allclose(q3.z, expected.z))

    def test_Quaternion_MultiplyVector(self):
        q = Quaternion(0.5, 0.5, 0.5, 0.5)
        v = np.array([1.0, 1.0, 1.0])
        v2 = Quaternion.MultiplyVector(q, v)
        expected = np.array([1.0, 1.0, 1.0])
        self.assertTrue(np.allclose(v2, expected))

    def test_Quaternion_FromEuler(self):
        e = np.array([45.0, 45.0, 45.0])
        q = Quaternion.FromEuler(e[0], e[1], e[2])
        expected = Quaternion(0.5, 0.5, 0.5, 0.5)
        self.assertTrue(np.allclose(q.w, expected.w))
        self.assertTrue(np.allclose(q.x, expected.x))
        self.assertTrue(np.allclose(q.y, expected.y))
        self.assertTrue(np.allclose(q.z, expected.z))

if __name__ == '__main__':
    unittest.main()