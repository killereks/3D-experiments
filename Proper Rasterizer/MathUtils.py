import numpy as np

from perlin_noise import PerlinNoise

from Mesh import Mesh

from custom_logging import LOG

class MathUtils:
    @staticmethod
    def GenerateNoiseMap(width: int, height: int, scale: float, offset: np.ndarray):
                        
        noise = PerlinNoise(octaves=8)
        
        noiseMap = np.zeros((width, height))

        for y in range(height):
            for x in range(width):
                sampleX = (x + offset[0]) / scale
                sampleY = (y + offset[1]) / scale

                noiseMap[x, y] = noise([sampleX, sampleY])

        return noiseMap

    @staticmethod
    def InverseLerp(a: float, b: float, value: float):
        return (value - a) / (b - a)

    @staticmethod
    def Lerp(a: float, b: float, t: float):
        return a + t * (b - a)

    @staticmethod
    def ProceduralQuad(heightMap: np.ndarray):
        vertices = []
        faces = []
        uvs = []
        
        print(heightMap)

        for y in range(len(heightMap)):
            for x in range(len(heightMap[y])):
                vertices.append([x, heightMap[y][x], y])
                uvs.append([x / len(heightMap[y]), y / len(heightMap)])

        for y in range(len(heightMap) - 1):
            for x in range(len(heightMap[y]) - 1):
                faces.append([x + y * len(heightMap[y]), x + 1 + y * len(heightMap[y]), x + 1 + (y + 1) * len(heightMap[y])])
                faces.append([x + y * len(heightMap[y]), x + 1 + (y + 1) * len(heightMap[y]), x + (y + 1) * len(heightMap[y])])

        quad_mesh = Mesh(np.array(vertices), np.array(faces), np.array([]), np.array(uvs))
        quad_mesh.recalculate_normals()
        quad_mesh.name = "Procedural Quad"

        return quad_mesh

        
