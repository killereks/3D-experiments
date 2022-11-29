from Mesh import Mesh

from OpenGL.GL import *

import time

import numpy as np

class PostProcessing:
    def __init__(self, shader, width, height):
        # list of shaders to apply one by one
        self.shader = shader

        self.width = width
        self.height = height
        
        self.fbo = glGenFramebuffers(1)
        self.texture = glGenTextures(1)
        self.rbo = glGenRenderbuffers(1)

        self.cameraDepthMap = 0

        self.shadow_map = None
        self.sun = None
        self.camera = None

        self.quad = Mesh.CreateScreenQuad()

        self.time_started = time.time()

        # initialize
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

        glBindTexture(GL_TEXTURE_2D, self.texture)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.texture, 0)

        glBindRenderbuffer(GL_RENDERBUFFER, self.rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.rbo)


    def draw(self):
        self.shader.use()

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.shadow_map)
        
        # self.rbo contains the z depth buffer
        # copy rbo framebuffer depth values into the depth map texture
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.cameraDepthMap)

        glUniform1i(self.shader.get_keyword("screenTexture"), 0)
        glUniform1i(self.shader.get_keyword("shadowMap"), 1)
        glUniform1i(self.shader.get_keyword("cameraDepthMap"), 2)
        
        glUniform3fv(self.shader.get_keyword("lightPos"), 1, self.sun.transform.position)

        # normalized light direction towards origin
        glUniform3fv(self.shader.get_keyword("lightDir"), 1, -self.sun.transform.position)
        glUniform3fv(self.shader.get_keyword("sunColor"), 1, self.sun.color)

        glUniformMatrix4fv(self.shader.get_keyword("view"), 1, GL_TRUE, self.camera.getViewMatrix())
        glUniformMatrix4fv(self.shader.get_keyword("projection"), 1, GL_TRUE, self.camera.projectionMatrix)

        glUniformMatrix4fv(self.shader.get_keyword("lightSpaceMatrix"), 1, GL_TRUE, self.sun.getLightSpaceMatrix())
        glUniformMatrix4fv(self.shader.get_keyword("lightModel"), 1, GL_TRUE, self.sun.getLightView())

        glUniform3fv(self.shader.get_keyword("camPos"), 1, -self.camera.transform.position)
        glUniform3fv(self.shader.get_keyword("camFwd"), 1, -self.camera.forward())
        glUniform3fv(self.shader.get_keyword("camUp"), 1, self.camera.up())
        glUniform3fv(self.shader.get_keyword("camRight"), 1, self.camera.right())

        glUniform1f(self.shader.get_keyword("time"), time.time() - self.time_started)

        self.quad.draw()

    def before_draw(self, shadow_map, sun, camera, cameraDepthMap):
        """
        Draw the scene to the texture
        """
        self.shadow_map = shadow_map
        self.sun = sun
        self.camera = camera
        self.cameraDepthMap = cameraDepthMap

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    
    def after_draw(self):
        """
        Draw the texture to the screen
        """
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        self.draw()