from OpenGL.GL import *
import pygame as pg

from custom_logging import LOG, LogLevel

from PIL import Image

import numpy as np

class Texture:
    def __init__(self):
        self.texture = None
        self.width = 0
        self.height = 0
        

    @staticmethod
    def Load(filepath: str):
        """
        Load a texture from a file

        :param filepath: The path to the file

        :return: The texture
        """

        tex = Texture()
        
        tex.texture = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, tex.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        image = pg.image.load(filepath).convert_alpha()
        image_width, image_height = image.get_rect().size
        img_data = pg.image.tostring(image, 'RGBA')

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        tex.width = image_width
        tex.height = image_height

        return tex
    
    def use(self, index: int):
        """
        Use the texture at the given index

        :param index: The index to use, must be between 0 and 31
        """
        if index >= 32:
            LOG("Texture index out of range", LogLevel.ERROR)
            return
        
        glActiveTexture(GL_TEXTURE0 + index)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def Save(self, filepath: str, format: str, opengl_format: int):
        """
        Save the texture to a file

        :param filepath: The path to the file
        """
        
        # read current texture pixels
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, self.width, self.height, opengl_format, GL_UNSIGNED_BYTE)

        #print(data)

        # create image
        image = Image.frombytes(format, (self.width, self.height), data)
        image.save(filepath)