from Quaternion import Quaternion
from perlin_noise import PerlinNoise

def RotateOverTime(object, dt):
    object.transform.rotation *= Quaternion.FromAxisAngle([0, 1, 0], dt * 10)

def ProceduralTerrain(obj):
    # go over every vertex and move it up and down
    noise = PerlinNoise(octaves=6, seed=1)

    for i in range(len(obj.vertices)):
        x = obj.vertices[i][0]
        y = obj.vertices[i][1]
        z = obj.vertices[i][2]

        scale = 0.5
        
        # get the noise value
        noise_value = noise([x * scale, y * scale, z * scale]) * 0.1

        # move the vertex up and down
        obj.vertices[i][1] = noise_value



    obj.recalculate_normals()


    

Programs = {
    "RotateOverTime": RotateOverTime,
    "ProceduralTerrain": ProceduralTerrain
}