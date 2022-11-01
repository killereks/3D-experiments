from Material import Material
import numpy as np

from custom_logging import LOG

class MaterialLibrary:
    def __init__(self, filename):
        self.materials = {}
        self.load(filename)

    def load(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if line.startswith('newmtl'):
                material_name = line.split()[1]
                self.materials[material_name] = Material()
            elif line.startswith('Ka'):
                self.materials[material_name].Ka = np.array([float(x) for x in line.split()[1:]])
            elif line.startswith('Kd'):
                self.materials[material_name].Kd = np.array([float(x) for x in line.split()[1:]])
            elif line.startswith('Ks'):
                self.materials[material_name].Ks = np.array([float(x) for x in line.split()[1:]])
            elif line.startswith('Ns'):
                self.materials[material_name].Ns = float(line.split()[1])
            elif line.startswith('Ni'):
                self.materials[material_name].Ni = float(line.split()[1])
            elif line.startswith('d'):
                self.materials[material_name].d = float(line.split()[1])
            elif line.startswith('illum'):
                self.materials[material_name].illum = int(line.split()[1])

        LOG(f"Loaded {len(self.materials)} materials from {filename}")

    def get_material(self, material_name):
        return self.materials[material_name]