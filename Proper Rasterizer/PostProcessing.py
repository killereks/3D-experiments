from Mesh import Mesh

from OpenGL.GL import *

class PostProcessing:
    def __init__(self, shader, width, height):
        # list of shaders to apply one by one
        self.shader = shader

        self.width = width
        self.height = height
        
        self.fbo = glGenFramebuffers(1)
        self.texture = glGenTextures(1)
        self.rbo = glGenRenderbuffers(1)

        self.shadow_map = None

        self.quad = Mesh.CreateScreenQuad()

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

        glUniform1i(self.shader.get_keyword("screenTexture"), 0)
        glUniform1i(self.shader.get_keyword("shadowMap"), 1)

        self.quad.draw()

    def before_draw(self, shadow_map):
        """
        Draw the scene to the texture
        """
        self.shadow_map = shadow_map

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    
    def after_draw(self):
        """
        Draw the texture to the screen
        """
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        self.draw()