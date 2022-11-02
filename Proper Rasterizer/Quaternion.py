from email import header
import numpy as np

class Quaternion:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

        self.Normalize()

    def __mul__(self, other):
        """
        Quaternion multiplication
        :param other: the other quaternion
        :return: the product of the two quaternions which represents the rotation of the other quaternion by this quaternion
        """
        lhs = self
        rhs = other
        
        w = lhs.w * rhs.w - lhs.x * rhs.x - lhs.y * rhs.y - lhs.z * rhs.z
        x = lhs.w * rhs.x + lhs.x * rhs.w + lhs.y * rhs.z - lhs.z * rhs.y
        y = lhs.w * rhs.y - lhs.x * rhs.z + lhs.y * rhs.w + lhs.z * rhs.x
        z = lhs.w * rhs.z + lhs.x * rhs.y - lhs.y * rhs.x + lhs.z * rhs.w

        return Quaternion(w, x, y, z)

    @staticmethod
    def Inverse(q):
        # such that q * q.Inverse() = 1
        # conjugate
        return Quaternion(q.w, -q.x, -q.y, -q.z)

    def Normalize(self):
        """
        Normalize the quaternion
        Needed because the quaternion is not normalized after multiplication
        Every operation needs to return a normalized quaternion
        """
        length = np.sqrt(self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z)
        self.w /= length
        self.x /= length
        self.y /= length
        self.z /= length

    def ToMatrix(self):
        """
        Convert the quaternion to a rotation matrix
        :return: the 3x3 rotation matrix
        """
        matrix = np.identity(4)
        matrix[0][0] = 1 - 2 * self.y ** 2 - 2 * self.z ** 2
        matrix[0][1] = 2 * self.x * self.y - 2 * self.z * self.w
        matrix[0][2] = 2 * self.x * self.z + 2 * self.y * self.w
        matrix[1][0] = 2 * self.x * self.y + 2 * self.z * self.w
        matrix[1][1] = 1 - 2 * self.x ** 2 - 2 * self.z ** 2
        matrix[1][2] = 2 * self.y * self.z - 2 * self.x * self.w
        matrix[2][0] = 2 * self.x * self.z - 2 * self.y * self.w
        matrix[2][1] = 2 * self.y * self.z + 2 * self.x * self.w
        matrix[2][2] = 1 - 2 * self.x ** 2 - 2 * self.y ** 2
        return matrix

    def ToEuler(self):
        """
        Convert the quaternion to Euler angles

        Formula from https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles

        :return: the Euler angles in degrees
        """
        x = np.arctan2(2 * self.y * self.w - 2 * self.x * self.z, 1 - 2 * self.y ** 2 - 2 * self.z ** 2)
        y = np.arcsin(2 * self.x * self.y + 2 * self.z * self.w)
        z = np.arctan2(2 * self.x * self.w - 2 * self.y * self.z, 1 - 2 * self.x ** 2 - 2 * self.z ** 2)

        x = np.degrees(x)
        y = np.degrees(y)
        z = np.degrees(z)

        return np.array([x, y, z])

    @staticmethod
    def identity():
        return Quaternion(1, 0, 0, 0)

    @staticmethod
    def MultiplyVector(q, v):
        # q * Quaternion(0, v[0], v[1], v[2]) * q.Inverse()
        
        x = q.w * v[0] + q.y * v[2] - q.z * v[1]
        y = q.w * v[1] + q.z * v[0] - q.x * v[2]
        z = q.w * v[2] + q.x * v[1] - q.y * v[0]
        w = -q.x * v[0] - q.y * v[1] - q.z * v[2]

        return np.array(
            [w * q.x + x * q.w - y * q.z + z * q.y,
             w * q.y + y * q.w - z * q.x + x * q.z,
             w * q.z + z * q.w - x * q.y + y * q.x],"f")


    @staticmethod
    def FromEuler(x, y, z):
        t0 = np.cos(np.radians(z) * 0.5)
        t1 = np.sin(np.radians(z) * 0.5)
        t2 = np.cos(np.radians(x) * 0.5)
        t3 = np.sin(np.radians(x) * 0.5)
        t4 = np.cos(np.radians(y) * 0.5)
        t5 = np.sin(np.radians(y) * 0.5)

        w = t0 * t2 * t4 + t1 * t3 * t5
        x = t0 * t3 * t4 - t1 * t2 * t5
        y = t0 * t2 * t5 + t1 * t3 * t4
        z = t1 * t2 * t4 - t0 * t3 * t5

        return Quaternion(w, x, y, z)

    @staticmethod
    def FromAxisAngle(axis, angle):
        axis = axis / np.linalg.norm(axis)
        angle = np.radians(angle)
        s = np.sin(angle / 2)
        return Quaternion(np.cos(angle / 2), axis[0] * s, axis[1] * s, axis[2] * s)


    def __str__(self):
        euler = self.ToEuler()
        # 3 decimal places, align each column to center using ^, and use a space as a fill character
        return f"Quaternion (wxyz): {self.w:^8.3f} {self.x:^8.3f} {self.y:^8.3f} {self.z:^8.3f} \nEuler(xyz): {euler[0]:^8.3f} {euler[1]:^8.3f} {euler[2]:^8.3f}"

