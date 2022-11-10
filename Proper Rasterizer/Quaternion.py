import numpy as np
import Quaternion

class Quaternion:
    def __init__(self, w: float, x: float, y: float, z: float):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

        self.Normalize()

    def __mul__(self, other: Quaternion):
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
    def Inverse(q: Quaternion):
        """
        Inverse of a quaternion, such that q * q.Inverse() = q.Identity()
        :param q: the quaternion to invert
        """
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
        x = np.arctan2(2 * (self.w * self.x + self.y * self.z), 1 - 2 * (self.x ** 2 + self.y ** 2))
        y = np.arcsin(2 * (self.w * self.y - self.z * self.x))
        z = np.arctan2(2 * (self.w * self.z + self.x * self.y), 1 - 2 * (self.y ** 2 + self.z ** 2))

        x = np.degrees(x)
        y = np.degrees(y)
        z = np.degrees(z)

        return np.array([x, y, z],"f")

    @staticmethod
    def identity():
        """
        Quaternion that represents no rotation
        :return: the identity quaternion
        """
        return Quaternion(1, 0, 0, 0)

    @staticmethod
    def MultiplyVector(q: Quaternion, v: np.ndarray):
        """
        Rotate a vector by a quaternion
        
        :param q: the quaternion to rotate by
        :param v: the vector to rotate
        """
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
    def FromEuler(x: float, y: float, z: float):
        """
        Convert Euler angles to a quaternion
        :param x: the x angle in degrees
        :param y: the y angle in degrees
        :param z: the z angle in degrees
        :return: the quaternion
        """

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
    def FromAxisAngle(axis: np.ndarray, angle: float):
        """
        Create a quaternion from an axis and an angle
        :param axis: the axis of rotation
        :param angle: the angle of rotation in degrees
        """
        axis = axis / np.linalg.norm(axis)
        angle = np.radians(angle)
        s = np.sin(angle / 2)
        return Quaternion(np.cos(angle / 2), axis[0] * s, axis[1] * s, axis[2] * s)

    @staticmethod
    def FromMatrix(matrix: np.ndarray):
        """
        Create a quaternion from a 3x3 rotation matrix
        :param matrix: the rotation matrix
        """
        trace = matrix[0][0] + matrix[1][1] + matrix[2][2]
        if trace > 0:
            s = 0.5 / np.sqrt(trace + 1.0)
            return Quaternion(0.25 / s, (matrix[2][1] - matrix[1][2]) * s, (matrix[0][2] - matrix[2][0]) * s,
                              (matrix[1][0] - matrix[0][1]) * s)
        else:
            if matrix[0][0] > matrix[1][1] and matrix[0][0] > matrix[2][2]:
                s = 2.0 * np.sqrt(1.0 + matrix[0][0] - matrix[1][1] - matrix[2][2])
                return Quaternion((matrix[2][1] - matrix[1][2]) / s, 0.25 * s, (matrix[0][1] + matrix[1][0]) / s,
                                  (matrix[0][2] + matrix[2][0]) / s)
            elif matrix[1][1] > matrix[2][2]:
                s = 2.0 * np.sqrt(1.0 + matrix[1][1] - matrix[0][0] - matrix[2][2])
                return Quaternion((matrix[0][2] - matrix[2][0]) / s, (matrix[0][1] + matrix[1][0]) / s, 0.25 * s,
                                  (matrix[1][2] + matrix[2][1]) / s)
            else:
                s = 2.0 * np.sqrt(1.0 + matrix[2][2] - matrix[0][0] - matrix[1][1])
                return Quaternion((matrix[1][0] - matrix[0][1]) / s, (matrix[0][2] + matrix[2][0]) / s,
                                  (matrix[1][2] + matrix[2][1]) / s, 0.25 * s)

    @staticmethod
    def LookRotation(forward: np.ndarray, up: np.ndarray):
        """
        Create a quaternion from a forward and up vector
        :param forward: the forward vector
        :param up: the up vector
        """
        forward = forward / np.linalg.norm(forward)
        up = up / np.linalg.norm(up)
        right = np.cross(forward, up)
        up = np.cross(right, forward)

        m = np.array([right, up, forward],"f")
        return Quaternion.FromMatrix(m)

    def __str__(self):
        euler = self.ToEuler()
        # 3 decimal places, align each column to center using ^, and use a space as a fill character
        return f"Quaternion (wxyz): {self.w:^8.3f} {self.x:^8.3f} {self.y:^8.3f} {self.z:^8.3f} \nEuler(xyz): {euler[0]:^8.3f} {euler[1]:^8.3f} {euler[2]:^8.3f}"

