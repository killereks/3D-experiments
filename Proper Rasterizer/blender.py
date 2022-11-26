import numpy as np
from custom_logging import LOG, LogLevel

import Mesh

def load_obj_file(file_name: str):
	"""
	Loads an obj file and returns the vertices, faces, normals and texture coordinates

	:param file_name: The path to the obj file
	:return: A tuple of vertices, faces, normals and texture coordinates
	"""
	
	LOG(f"Attemping to load {file_name}")
	
	vertices = []
	normals = []
	texcoords = []
	faces = []

	with open(file_name) as objfile:
		# loop over all lines in the file

		for line in objfile:
			line = line.strip()
			# skip empty lines
			if not line: continue

			# split the line into labels
			label = line.split()

			# skip comments
			if label[0] == '#': continue
			
			# vertex
			if label[0] == 'v':
				vertices.append([float(x) for x in label[1:]])
			
			# vertex normal
			elif label[0] == 'vn':
				normals.append([float(x) for x in label[1:]])

			# texture coordinate
			elif label[0] == 'vt':
				texcoords.append([float(x) for x in label[1:]])

			# face
			elif label[0] == 'f':
				# parse the face
				face = []
				for v in label[1:]:
					# split the vertex into its components
					v = v.split('/')
					# the first component is the vertex index
					face.append(int(v[0]) - 1)
				# add the face to the list of faces
				faces.append(face)

		# convert to numpy arrays
		vertices = np.array(vertices, dtype='f')
		normals = np.array(normals, dtype='f')

		if len(texcoords) == 0:
			texcoords = np.zeros((len(vertices), 2))
			LOG("No texture coordinates found, using default texture coordinates", LogLevel.WARNING)
		else:
			texcoords = np.array(texcoords, dtype='f')
		
		faces = np.array(faces, dtype=np.uint32)

		LOG(f"Loaded {file_name} with {len(vertices):,} vertices, {len(normals):,} normals, {len(texcoords):,} texcoords, and {len(faces):,} faces")

		return vertices, faces, normals, texcoords

def load_mesh(file_name: str):
	"""
	Loads a mesh from an obj file

	:param file_name: The path to the obj file
	:return: A Mesh object
	"""
	vertices, faces, normals, texcoords = load_obj_file(file_name)

	return Mesh.Mesh(vertices, faces, normals, texcoords)