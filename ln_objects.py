__author__ = 'ajtag'
import pygame
from random import randint, choice
import colorsys
import numpy as np
import xml.etree.ElementTree as ET
from numpy import pi, sin, cos

import logging

white = 255, 255, 255
black = 0, 0, 0


def hls_to_rgb(hue, lightness, saturation):
    return np.array(colorsys.hls_to_rgb(hue/360, lightness/100, saturation/100)) * 255


class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((x, y))
        self.image.set_colorkey(white)
        self.image.fill(white)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.info('##init##')


class Lamp:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Ceiling:
    lamps = []
    mask = None

    width = 0
    height = 0
    positions = {'NORTH':(0,0), 'SOUTH':(0,0), 'WEST':(0,0), 'EAST':(0,0), 'TAIL':(0,0)}



    def __init__(self, x, y):
        self.mask = pygame.Surface((x, y))
        self.mask.set_colorkey(white)
        self.parse_imagemask()


    def get_named_position(self, name):
        return self.positions[name]

    def parse_imagemask(self):

        tree = ET.parse('Resources/LS-TRIN-0023 East Mall.svg')
        root = tree.getroot()
        groups = root.findall('{http://www.w3.org/2000/svg}g')

        self.width = float(root.attrib['width']) * 1.2
        self.height = float(root.attrib['height']) * 1.2

        mnlx, mxlx, mnly, mxly = None, None, None, None

        tmplamps = []

        for g in groups:
            paths = g.findall('{http://www.w3.org/2000/svg}path')

            if mnlx is None:
                mnlx = float(paths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx'])
                mxlx = float(paths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx'])
                mnly = float(paths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy'])
                mxly = float(paths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy'])

            for p in paths:
                lampx = float(p.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx'])
                lampy = float(p.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy'])

                mnlx = min(mnlx, lampx)
                mxlx = max(mxlx, lampx)
                mnly = min(mnly, lampy)
                mxly = max(mxly, lampy)

                tmplamps.append((lampx, lampy))


        mnlx -= 5
        mxlx += 5
        mnly -= 5
        mxly += 5

        _,_,x,y = list(self.mask.get_rect())
        for lamp in tmplamps:
            self.lamps.append(
                Lamp((lamp[0] - mnlx)/(mxlx - mnlx) * x,(lamp[1] - mnly)/(mxly - mnly) * y))
            pos = pygame.Rect(
                (lamp[0] - mnlx)/(mxlx - mnlx) * x,(lamp[1] - mnly)/(mxly - mnly) * y, 3, 3)
            pygame.draw.rect(self.mask, white, pos, 0)



        self.positions['NORTH'] = ((self.width/2 - mnlx)/(mxlx - mnlx) * x, 0)
        self.positions['SOUTH'] = ((self.width/2 - mnlx)/(mxlx - mnlx) * x, (self.height - mnly)/(mxly - mnly) * y)
        self.positions['WEST'] = (0, (self.height/2 - mnly)/(mxly - mnly) * y)
        self.positions['EAST'] = ((self.width - mnlx)/(mxlx - mnlx) * x, (self.height/2 - mnly)/(mxly - mnly) * y)






class Star(Sprite):
    #TODO: shooting star

    def __init__(self, lamp, starsize=5):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self, 2*starsize, 2*starsize)
        self.starsize = starsize

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.rect = (lamp.x-starsize/2, lamp.y-starsize/2, 2*starsize, 2*starsize)

        self.color = white
        self.rand_color()

        self.lamp = lamp

        self.log.info('created star at {},{}'.format(self.lamp.x-starsize/2, lamp.y-starsize/2))

    def rand_color(self):
        self.color = hls_to_rgb(randint(40, 60), randint(20, 100), randint(80, 100))

    def update(self):
        pygame.draw.circle(self.image, self.color, (self.starsize, self.starsize), self.starsize)


class StarrySky(pygame.sprite.Group):
    def __init__(self, size, ceiling):
        self.log = logging.getLogger(self.__class__.__name__)
        pygame.sprite.Group.__init__(self)
        self.ceiling = ceiling
        self.alpha = 0
        self.dalpha = 2

        self.s = pygame.Surface(size)
        self.s.set_colorkey(white)
        #self.s.

    def update(self):
        self.alpha = min(255, max(0, self.alpha + self.dalpha))
        self.s.set_alpha(self.alpha)

        r = randint(0, 100)
        if r < 15:
            self.log.info('add star')
            l = randint(0, len(self.ceiling.lamps)-1)
            try:
                self.add(Star(self.ceiling.lamps[l]))
            except:
                self.log.info(l, len(self.ceiling.lamps))

        elif r == 99:
            self.log.info('add Shooting Star')
        pygame.sprite.Group.update(self)

    def draw(self, surface):
        self.s.fill(white)
        pygame.sprite.Group.draw(self, self.s)
        surface.blit(self.s, (0, 0))

    def end(self):
        self.log.info('Fade Stars Out')
        self.dalpha = -5
        pass


class RisingSun(Sprite):
    chordlengths = []

    def __init__(self,x,y, path,  max_radius=200, min_radius=50):
        """
        path should be a pygame.Rect, sun will arc from bottom left to top right
        :param path: pygame.Rect
        :param max_radius:
        :param min_radius:
        :return:
        """

        # Call the parent class (Sprite) constructor
        Sprite.__init__(self, max_radius*2, max_radius*2)

        ## init rect

        self.path = path
        #self.x, self.y = x, y
        self.rect = self.image.get_rect()
        #self.xy=pygame.Rect(x,y, )

        self.max_radius = max_radius
        self.min_radius = min_radius
        self.radius = self.max_radius

        self.log.info('initing sun')

        #self.update_rect()
        self.height = 0
        self.update_chords()

    def set_height(self, time):
        """
        float between 0 and 1
        :param time:
        :return:
        """

        self.height = sin(time * pi/2)
        self.set_radius(self.max_radius - (self.height * (self.max_radius - self.min_radius)))

        self.rect.center = (
            self.path.left + (self.height * self.path.width),
            (self.path.bottomleft[1]) - (self.height * self.path.height)
        )

        self.update_chords()

    def update_chords(self):
        #chordlengths
        self.chordlengths = [2 * np.power(((self.radius * self.radius) - (d * d)), 0.5) for d in range(0, int(self.radius))]

    def set_radius(self, r):
        self.radius = r
        self.update_chords()
        self.rect.width = 2*r
        self.rect.height = 2*r

        self.image = pygame.Surface(self.rect.size)
        self.image.set_colorkey(white)

    #def update_rect(self):
    #    self.rect = (self.x, self.y, self.radius*2, self.radius*2)

    def draw(self, surface):
        self.image.fill(white)
        for n, d in enumerate(self.chordlengths):
            c = height_color(self.height)
            pygame.draw.aaline(self.image, c, (self.radius - d/2, (self.radius + n)), (((2*self.radius) - (self.radius-d/2)), (self.radius + n)), True)
            c = height_color(self.height)
            pygame.draw.aaline(self.image, c, (self.radius - d/2, (self.radius - n)), (((2*self.radius) - (self.radius-d/2)), (self.radius - n)), True)

        surface.blit(self.image, (self.rect.topleft[0], self.rect.topleft[1]))

def height_color(height):
        # height = 0:pi * 4/6
        height_hue = int(np.sin(height) * 40 * 6 / 4/ pi)
        height_lum = int(np.sin(height) * 6/4/pi*50)

        height_hue = (350 + randint(height_hue, (height_hue+20))) % 360
        height_lum = 40 + randint(height_lum, height_lum+10)

        return hls_to_rgb(height_hue, height_lum, randint(90, 100))

class Clouds(pygame.sprite.Group):
    def __init__(self, size):
        self.log = logging.getLogger(self.__class__.__name__)
        pygame.sprite.Group.__init__(self)
        self.s = pygame.Surface(size)
        self.s.set_colorkey(white)

        self.angryness = 0
        self.starteast = 0
        self.gowest = 2

        self.wait = 0

    def update(self):
        if self.wait == 0:
            self.log.info('adding new cloud {}, {}, angry:{}'.format(self.starteast, self.gowest, self.angryness))
            self.angryness += 0.05

            if self.angryness >= 1:
                self.angryness = 0

            self.starteast = abs(self.starteast - 800)
            self.gowest = -self.gowest


            self.add(Cloud(pygame.Rect(self.starteast, 250, self.gowest, 0), angryness=self.angryness, radius=randint(1,5)*40))

        if self.wait == 100:
            self.wait = 0
        else:
            self.wait +=1

        pygame.sprite.Group.update(self)

    def draw(self, surface):
        self.s.fill(white)
        pygame.sprite.Group.draw(self, self.s)
        surface.blit(self.s, (0, 0))

    def end(self):
        self.log.info('Fade clouds Out')

class Cloud(pygame.sprite.Sprite):
    def __init__(self, location, angryness=0.5, radius=50):
        """

        :param location: pygame.Rect
        :param angryness: float
        :param radius: int
        :return:
        """
        # Call the parent class (Sprite) constructor
        self.set_angryness(angryness)
        self.radius = radius
        self.rect = location
        Sprite.__init__(self, self.radius * 2, self.radius * 2)

    def update(self):
        self.draw()
        self.rect.move_ip((self.rect.width, self.rect.height))

    def draw(self):
        print('draw')
        self.image.fill(white)
        pygame.draw.circle(self.image, self.colour, (self.radius,self.radius), self.radius)
        #surface.blit(self.image, (0, 0))  # motion vector not passed as rect as may be -ve area

    def set_angryness(self, angryness):
        """
        value between 0 and 1
        :param angryness:float
        :return:
        """
        if angryness < 0 or angryness > 1:
            raise ValueError

        self.angryness = angryness

        h = 194
        s = randint(10, 20)
        l = 90 -(angryness * 80)

        self.colour = hls_to_rgb(h,l,s)



class Thunderstorm(pygame.sprite.Group):
    def __init__(self, size, ceiling):
        self.log = logging.getLogger(self.__class__.__name__)
        pygame.sprite.Group.__init__(self)
        self.s = pygame.Surface(size)
        self.s.set_colorkey(white)

class Lightning(pygame.sprite.Sprite):
    def __init__(self, ):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)


class SheetLighting(Lightning):
    color = (255, 36, 251)

class ForkLighting(Lightning):
    color = (246, 255, 71)

class Splash(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

class Wave(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

class Bouy(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.colour = choice('red', 'green')


class Bird(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

class ForestCanopey(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

class Aurora(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

class Constallation(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

class HSMoon(Sprite):
    #uri = 'Resources/hackspace_logo_large.svg'
    polyH = 'd="m 239.49266,250.00824 -50.5176,-50.51229 -17.0112,15 -7.9137,-7.05176 43.3907,-43.39074 7.0518,7.86654 -15.2381,16.35968 51.4099,51.54116 76.3241,-76.32409 -51.4562,-51.4562 -9.0798,8.91118 -60.4157,-60.41567 8.9112,-9.07983 L 163.49186,0 87.08205,76.40981 l 51.65436,51.29688 16.32015,-15.21074 9.891,9.03928 -43.41564,43.41569 -9.03928,-9.93821 15,-16.98438 L 76.99521,87.49595 0,163.49846 l 51.45291,51.4529 9.07983,-8.91118 60.41567,60.41567 -8.90631,9.07487 51.43836,50.96523 z"'


    def __init__(self, x = 300, y=300, r=150):
        Sprite.__init__()
        # Call the parent class (Sprite) constructor
        self.x, self.y, self.radius = x,y,r
        self.logo = pygame.image.load(self.uri)

    def draw(self):
        pass





