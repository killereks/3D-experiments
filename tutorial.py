import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr

WIDTH = 1920
HEIGHT = 1080

class Cube:
    def __init__(self, position, eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class App:
    def __init__(self):
        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((WIDTH,HEIGHT), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

        self.cube_mesh = Mesh("models/monkey.obj")

        #initialise opengl
        glClearColor(0.1, 0.2, 0.2, 1)
        
        self.shader = self.createShader("shaders/vertex.glsl", "shaders/fragment.glsl")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        glEnable(GL_DEPTH_TEST)

        self.wood_texture = Material("textures/checker.jpg")

        self.cube = Cube(
            position = [0,0,-5],
            eulers = [0,0,0]
        )

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = WIDTH/HEIGHT, 
            near = 0.1, far = 10, dtype=np.float32
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader,"projection"),
            1, GL_FALSE, projection_transform
        )
        self.modelMatrixLocation = glGetUniformLocation(self.shader,"model")
        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def mainLoop(self):
        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            
            #update cube
            self.cube.eulers[2] += 0.25
            if self.cube.eulers[2] > 360:
                self.cube.eulers[2] -= 360
            
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)

            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            """
                pitch: rotation around x axis
                roll:rotation around z axis
                yaw: rotation around y axis
            """
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.cube.eulers), dtype=np.float32
                )
            )
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_translation(
                    vec=np.array(self.cube.position),dtype=np.float32
                )
            )
            glUniformMatrix4fv(self.modelMatrixLocation,1,GL_FALSE,model_transform)
            self.wood_texture.use()
            glBindVertexArray(self.cube_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)

            # display fps
            pg.display.set_caption("FPS: {}".format(self.clock.get_fps()))

            pg.display.flip()

            #timing
            self.clock.tick(165)
        self.quit()

    def quit(self):
        self.cube_mesh.destroy()
        self.wood_texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class Mesh:
    def __init__(self, filepath):
        # x, y, z, s, t
        self.vertices = self.loadMesh(filepath)

        self.vertex_count = len(self.vertices)//5
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
    
    def loadMesh(self, filepath):
        vertices = []

        v = []
        vt = []
        vn = []

        with open(filepath, "r") as f:
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[:firstSpace]

                if flag == "v":
                    line = line.replace("v ","")
                    line = line.split(" ")
                    l = [float(i) for i in line]
                    v.append(l)
                elif flag == "vt":
                    line = line.replace("vt ","")
                    line = line.split(" ")
                    l = [float(i) for i in line]
                    vt.append(l)
                elif flag == "vn":
                    line = line.replace("vn ","")
                    line = line.split(" ")
                    l = [float(i) for i in line]
                    vn.append(l)
                elif flag == "f":
                    # face, three or more vertices in v/vt/vn form
                    line = line.replace("f ","")
                    line = line.replace("\n","")
                    line = line.split(" ")

                    faceVertices = []
                    faceTextures = []
                    faceNormals = []

                    for vertex in line:
                        vertex = vertex.split("/")
                        position = int(vertex[0])-1
                        texture = int(vertex[1])-1
                        normal = int(vertex[2])-1
                        faceVertices.append(v[position])
                        faceTextures.append(vt[texture])
                        faceNormals.append(vn[normal])

                    triangles_in_face = len(line) - 2
                    vertex_order = []
                    for i in range(triangles_in_face):
                        vertex_order.append(0)
                        vertex_order.append(i+1)
                        vertex_order.append(i+2)
                    
                    for i in vertex_order:
                        for x in faceVertices[i]:
                            vertices.append(x)
                        for x in faceTextures[i]:
                            vertices.append(x)
                        for x in faceNormals[i]:
                            vertices.append(x)


                line = f.readline()

        return vertices


    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class Material:
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

myApp = App()