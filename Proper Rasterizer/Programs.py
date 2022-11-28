from Quaternion import Quaternion
from perlin_noise import PerlinNoise

from custom_logging import LOG, LogLevel

import numpy as np

from Texture import Texture

import time

from OpenGL.GL import *

from PIL import Image

import matplotlib.pyplot as plt

def RotateOverTime(object, dt):
    object.transform.rotation *= Quaternion.FromAxisAngle([0, 1, 0], dt * 10)

def ProceduralTerrain(obj):
    # go over every vertex and move it up and down
    noise = PerlinNoise(octaves=4, seed=10)

    boundsY = np.zeros(2)
    heightBounds = np.zeros(2)

    size = int(np.sqrt(obj.vertices.shape[0]))
    
    heights = np.zeros((size, size))

    for i in range(len(obj.vertices)):
        perc = i / len(obj.vertices) * 100
        if i % (len(obj.vertices) // 100) == 0:
            LOG(f"Generating Island... {perc:.0f}%", LogLevel.WARNING, True)

        x = obj.vertices[i][0]
        y = obj.vertices[i][1]
        z = obj.vertices[i][2]
        
        dist = x * x + z * z

        scale = 0.5
        
        # get the noise value
        noise_value = (noise([x * scale, y * scale, z * scale]) + 1) * 0.2 * 0.5

        height = noise_value - dist * 0.15

        boundsY = np.array([min(boundsY[0], height), max(boundsY[1], height)])
        heightBounds = np.array([min(heightBounds[0], height), max(heightBounds[1], height)])

        #heights[indexX, indexY] = height

        index_x = int(i % size)
        index_y = int(i / size)
        heights[index_x, index_y] = height

        # move the vertex up and down
        obj.vertices[i][1] = height

    scaleY = obj.transform.scale[1]
    LOG(f"Island Generated! Noise-Bounds: {boundsY[0]} - {boundsY[1]}. Height-Bounds: {heightBounds[0]*scaleY} - {heightBounds[1]*scaleY}", LogLevel.WARNING)

    # save heights to image
    heights = np.array(heights)
    # normalize heights
    heights = (heights - boundsY[0]) / (boundsY[1] - boundsY[0])
    heights = (heights * 255).astype(np.uint8)

    img = Image.fromarray(heights, 'L')
    img.save("textures/heightmap.png")
    LOG("Heightmap saved to heightmap.png", LogLevel.WARNING)

    obj.recalculate_normals()

def ScaleAnimation(object, dt):
    object.transform.scale = np.array([1,1,1]) * np.sin(time.time() * 4) * 0.5 + 1.5


Programs = {
    "RotateOverTime": RotateOverTime,
    "ProceduralTerrain": ProceduralTerrain,
    "ScaleAnimation": ScaleAnimation
}