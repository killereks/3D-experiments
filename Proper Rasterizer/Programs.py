from Quaternion import Quaternion
from perlin_noise import PerlinNoise

from custom_logging import LOG, LogLevel

import numpy as np

import time

def RotateOverTime(object, dt):
    object.transform.rotation *= Quaternion.FromAxisAngle([0, 1, 0], dt * 10)

def ProceduralTerrain(obj):
    # go over every vertex and move it up and down
    noise = PerlinNoise(octaves=4, seed=10)

    boundsY = np.zeros(2)

    for i in range(len(obj.vertices)):
        perc = i / len(obj.vertices) * 100
        if i % (len(obj.vertices) // 100) == 0:
            LOG(f"Generating Island... {perc:.0f}%", LogLevel.WARNING, True)

        x = obj.vertices[i][0]
        y = obj.vertices[i][1]
        z = obj.vertices[i][2]

        scale = 0.5
        
        # get the noise value
        noise_value = (noise([x * scale, y * scale, z * scale]) + 1) * 0.2 * 0.5

        # apply a distance based falloff so that the noise creates an island
        distance = np.linalg.norm(obj.vertices[i])
        falloff = 1 - np.clip(distance / 25, 0, 1)
        falloff = 1

        height = (noise_value + 1) * falloff

        boundsY = np.array([min(boundsY[0], height), max(boundsY[1], height)])

        # move the vertex up and down
        obj.vertices[i][1] = height

    LOG(f"Island Generated! Y-Bounds: {boundsY[0]} - {boundsY[1]}", LogLevel.WARNING, True)

    obj.recalculate_normals()

def ScaleAnimation(object, dt):
    object.transform.scale = np.array([1,1,1]) * np.sin(time.time() * 4) * 0.5 + 1.5


Programs = {
    "RotateOverTime": RotateOverTime,
    "ProceduralTerrain": ProceduralTerrain,
    "ScaleAnimation": ScaleAnimation
}