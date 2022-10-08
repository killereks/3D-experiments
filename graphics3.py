# imports all openGL functions
from OpenGL.GL import *

# pygame is just used to create a window with the operating system on which to draw.
import pygame

# we will use numpy to store data in arrays
import numpy as np

import time
import math
import random

from OpenGL.GLU import *

#https://github.com/alecjacobson/common-3d-test-models

class Scene:
    '''
    This is the main class for drawing an OpenGL scene using the PyGame library
    '''
    def __init__(self):
        '''
        Initialises the scene
        '''

        self.window_size = (800,600)

        # the first two lines initialise the pygame window. You could use another library for this,
        # for example GLut or Qt
        pygame.init()
        screen = pygame.display.set_mode(self.window_size, pygame.OPENGL | pygame.DOUBLEBUF, 24)

        glEnable(GL_DEPTH_TEST)

        gluPerspective(45, (self.window_size[0]/self.window_size[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -2.0)

        # Here we start initialising the window from the OpenGL side
        glViewport(0, 0, self.window_size[0], self.window_size[1])

        # this selects the background colour
        glClearColor(0.0, 0.5, 0.5, 1.0)

        self.camera = Camera(self.window_size)

        # This class will maintain a list of models to draw in the scene,
        # we will initalise it to empty
        self.models = []

    def add_model(self,model):
        '''
        This method just adds a model to the scene.
        :param model: The model object to add to the scene
        :return: None
        '''
        self.models.append(model)

    def draw(self):
        '''
        Draw all models in the scene
        :return: None
        '''

        # first we need to clear the scene
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # saves the current position
        glPushMatrix()

        # apply the camera parameters
        self.camera.apply()

        # then we loop over all models in the list and draw them
        for model in self.models:
            model.draw()

        # retrieve the last saved position
        glPopMatrix()

        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.
        pygame.display.flip()

    def update(self):
        for model in self.models:
            model.update()


    def keyboard(self, event):
        if event.key == pygame.K_q:
            self.running = False

        elif event.key == pygame.K_0:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);

        elif event.key == pygame.K_1:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);


        self.camera.keyboard(event)

    def run(self):
        '''
        Draws the scene in a loop until exit.
        '''

        clock = pygame.time.Clock()

        # We have a classic program loop
        running = True
        while running:

            # check whether the window has been closed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # keyboard events
                elif event.type == pygame.KEYDOWN:
                    self.keyboard(event)

                elif False and event.type == pygame.MOUSEMOTION:
                    if pygame.MOUSEBUTTONDOWN:
                        dx, dy = event.rel
                        self.camera.position[0] -= dx / self.window_size[0] /10 - 0.5
                        self.camera.position[1] -= dy / self.window_size[1] /10- 0.5

            self.update()
            # otherwise, continue drawing
            self.draw()

            clock.tick(600)

            print(clock.get_fps())


class TestModel:
    '''
    Base class for all models, implementing the basic draw function for triangular meshes.
    Inherit from this to create new models.
    '''

    def __init__(self, model_path, position=[0,0,0], orientation=[0,1,0], scale=1, color=[1,1,1]):
        '''
        Initialises the model data
        '''

        # store the object's color
        self.color = color

        # store the position of the model in the scene, ...
        self.position = position

        # ... the orientation, ...
        self.orientation = orientation

        self.angle = 180

        self.vertices, self.triangles = load_model(model_path)

        # ... and the scale factor
        if np.isscalar(scale):
            self.scale = [scale,scale,scale]
        else:
            self.scale = scale


    def applyParameters(self):
        # apply the position and orientation of the object
        glTranslate(*self.position)
        glRotate(self.angle, self.orientation[0], self.orientation[1], self.orientation[2])

        # apply scaling across all dimensions
        glScale(*self.scale)

        # then set the colour
        glColor(self.color)

    def draw(self):
        '''
        Draws the model using OpenGL functions
        :return:
        '''

        # saves the current pose parameters
        glPushMatrix()

        self.applyParameters()

        # Here we will use the simple GL_TRIANGLES primitive, that will interpret each sequence of
        # 3 vertices as defining a triangle.
        glBegin(GL_TRIANGLES)

        # we loop over all vertices in the model
        for triangle_set in self.triangles:
            #glColor3fv(color)
            # This function adds the vertex to the list
            #glVertex(vertex)

            # grab the positions of our triangle corners
            v1 = self.vertices[triangle_set[0]]
            v2 = self.vertices[triangle_set[1]]
            v3 = self.vertices[triangle_set[2]]

            # calculate light, we calculate directions from a single point to other 2 points
            # this is used in the cross product to give us a normal
            dir1 = normalize(sub(v2,v1))
            dir2 = normalize(sub(v3,v1))
            # we have two directions of the triangles, we can now get a normal
            normal = cross(dir1, dir2)
            # animate light using t
            t = 2.2
            #t = time.time()
            # circular motion for light
            light_dir = normalize([math.cos(t),math.sin(t),0])
            # simple light is calculated using dot between light dir and normalized normal (we need to normalize it so light
            # doesn't go above 1
            light_influence = dot(light_dir, normalize(normal))
            # here we make sure light does not go below 0 (we cannot have negative pixel colors)
            light_influence = max(0, light_influence)
            # multiply by light intensity to make it a bit brighter.
            light_intensity = 10
            light_influence *= light_intensity
            # tell opengl to color this triangle with a specific color
            color = [self.color[0] * light_influence, self.color[1] * light_influence, self.color[2] * light_influence]
            glColor3fv(color)
            # draw the triangle
            glVertex(v1)
            glVertex(v2)
            glVertex(v3)
           
        # the call to glEnd() signifies that all vertices have been entered.
        glEnd()

        # retrieve the previous pose parameters
        glPopMatrix()

        '''def applyPose(self):
            # apply the position and orientation and size of the object
            glScale(self.scale, self.scale, self.scale)
            glRotate(self.orientation[0], self.orientation[1], self.orientation[2], 1)
            glTranslate(*self.position)
            glColor(self.color)'''
   
    def update(self):
        self.angle += 1

class Camera:
    '''
    Basic class for handling the camera pose. At this stage, just x and y offsets.
    '''
    def __init__(self,size):
        self.size = size
        self.position = [0.0,0.0,0.0]

    def apply(self):
        '''5
        Apply the camera parameters to the current OpenGL context
        Note that this is the old fashioned API, we will use matrices in the
        future.
        '''
        glTranslate(*self.position)

    def keyboard(self,event):
        '''
        Handles keyboard events that are related to the camera.
        '''

        deltaPos = 0.1
       
        if event.key == pygame.K_PAGEDOWN:
            self.position[2] += deltaPos

        if event.key == pygame.K_PAGEUP:
            self.position[2] -= deltaPos

        if event.key == pygame.K_DOWN:
            self.position[1] += deltaPos

        if event.key == pygame.K_UP:
            self.position[1] -= deltaPos

        if event.key == pygame.K_LEFT:
            self.position[0] += deltaPos

        if event.key == pygame.K_RIGHT:
            self.position[0] -= deltaPos

# subtraction of two vectors
def sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

# normalize the vector
def normalize(vec):
    mag = vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2]

    return [vec[0] / mag, vec[1] / mag, vec[2] / mag]

# cross product of two vectors
def cross(a,b):
    x = a[1] * b[2] - b[1] * a[2]
    y = a[0] * b[2] - b[0] * a[2]
    z = a[0] * b[1] - b[0] * a[1]

    y = -y

    return [x,y,z]

# dot product of two vectors
def dot(a,b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def load_model(name):
    vertices = []
    triangles = []

    f = open(name,"r")
    lines = f.readlines()

    # v denotes a vertex position


    for line in lines:
        line_split = line.replace("\n","").split(" ")

        if line_split[0] == "v":
            vector = [
                    float(line_split[1]),
                    float(line_split[2]),
                    float(line_split[3])
                    ]
                   
            vertices.append(vector)
           
        # f denotes a face, which uses a vertex index, they are one indexed so we need to take one away
        elif line_split[0] == "f":
            triangle_set = [
                int(line_split[1])-1,
                int(line_split[2])-1,
                int(line_split[3])-1
                ]

            triangles.append(triangle_set)

    f.close()

    return vertices, triangles


if __name__ == '__main__':
    # initialises the scene object
    scene = Scene()

    # adds a few objects to the scene
    scene.add_model(TestModel("models/cow.txt",position=[0,0,-2], scale=0.3))
    #scene.add_model(TestModel("max.txt",position=[0,0,-5], scale=0.02))
    #scene.add_model(TestModel("cube.txt", position=[0,0,-5], scale=1))

    # starts drawing the scene
    scene.run()