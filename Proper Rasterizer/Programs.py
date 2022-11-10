from Quaternion import Quaternion

def RotateOverTime(object, dt):
    object.transform.rotation *= Quaternion.FromAxisAngle([0, 1, 0], dt * 10)

Programs = {
    "RotateOverTime": RotateOverTime
}