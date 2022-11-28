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

    @staticmethod
    def CreateFromHeights(heights, width, height):
        """
        Create a texture from a heightmap

        :param heights: The heightmap
        :param width: The width of the heightmap
        :param height: The height of the heightmap

        :return: The texture
        """
        tex = Texture()
        
        tex.texture = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, tex.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # heights is 1 channel, we need 3 channels
        data = []
        for i in range(len(heights)):
            data.append(heights[i])
            data.append(heights[i])
            data.append(heights[i])

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_FLOAT, data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        # save texture to image
        heights = np.array(heights)
        heights = heights.reshape((width, height))
        img = Image.fromarray(heights, 'L')
        img.save("heightmap.png")

        tex.width = width
        tex.height = height

        return tex

    def get_pixel(self, x: int, y: int) -> tuple:
        """
        Get the pixel at the given position

        :param x: The x position of the pixel
        :param y: The y position of the pixel

        :return: The pixel tuple (r,g,b) at the given position
        """

        if x >= self.width or y >= self.height:
            LOG("Pixel out of range", LogLevel.ERROR)
            return

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        data = glReadPixels(x, y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE)
        return data[0], data[1], data[2]

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