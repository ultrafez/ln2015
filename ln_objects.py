__author__ = 'ajtag'
import pygame
from random import randint, choice
import colorsys
import xml.etree.ElementTree as ET
from math import pi, sin, cos
import math
import os.path

import logging

white = 255, 255, 255
transparent = 255,255,255,0
black = 0, 0, 0


def hls_to_rgb(hue, lightness, saturation):
    return [i *255 for i in colorsys.hls_to_rgb(hue/360, lightness/100, saturation/100)]


class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.log = logging.getLogger(self.__class__.__name__)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((x, y))
        self.image.set_colorkey(white)
        self.image.fill(white)
        self.log.info('##init##')


class Group(pygame.sprite.Group):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        pygame.sprite.Group.__init__(self)


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
        tmplamps = []
        mnlx, mxlx, mnly, mxly = 10, 10, 10, 10

        img = pygame.image.load(os.path.join('Resources', 'Madrix.png'))
        x,y = img.get_rect().size
        for i in range(x):
            for j in range(y):
                if img.get_at((i,j))[0] == 255:
                    print(i,j)
                    mnlx = min(mnlx, i)
                    mxlx = max(mxlx, i)
                    mnly = min(mnly, j)
                    mxly = max(mxly, j)

                    tmplamps.append((i,j))



        self.update_lamps(tmplamps, mnlx, mxlx, mnly, mxly)



    def parse_imagemask_svg(self):
        tree = ET.parse(os.path.join('Resources','LS-TRIN-0023 East Mall.svg'))
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
            self.update_lamps(tmplamps, mnlx, mxlx, mnly, mxly)

    def update_lamps(self, tmplamps, mnlx, mxlx, mnly, mxly):


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


class StarrySky(Group):
    def __init__(self, size, ceiling):
        self.log = logging.getLogger(self.__class__.__name__)
        Group.__init__(self)
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
        Group.update(self)

    def draw(self, surface):
        self.s.fill(white)
        Group.draw(self, self.s)
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
        self.chordlengths = [2 * math.pow(((self.radius * self.radius) - (d * d)), 0.5) for d in range(0, int(self.radius))]

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
        height_hue = int(sin(height) * 40 * 6 / 4/ pi)
        height_lum = int(sin(height) * 6/4/pi*50)

        height_hue = (350 + randint(height_hue, (height_hue+20))) % 360
        height_lum = 40 + randint(height_lum, height_lum+10)

        return hls_to_rgb(height_hue, height_lum, randint(90, 100))

class Clouds(Group):
    def __init__(self, size):
        self.log = logging.getLogger(self.__class__.__name__)
        Group.__init__(self)
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

        Group.update(self)

    def draw(self, surface):
        self.s.fill(white)
        Group.draw(self, self.s)
        surface.blit(self.s, (0, 0))

    def end(self):
        self.log.info('Fade clouds Out')

class Cloud(Sprite):
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
        self.rect.move_ip((self.rect.width, self.rect.height))
        self.image.fill(white)
        pygame.draw.circle(self.image, self.colour, (self.radius,self.radius), self.radius)

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


class Raindrops(Group):
    def __init__(self, size):
        Group.__init__(self)
        self.s = pygame.Surface(size, pygame.SRCALPHA)
        self.s.set_colorkey(white)
        self.drop_frequency = 10
        self.count = 0
        self.s.set_alpha(100)
        self.alpha = 100

    def update(self):
        if len(self) < 5 and self.count % self.drop_frequency == 0:
            self.add(RainSplash(self.s.get_rect()))
        self.count = self.count + 1
        Group.update(self)

    def draw(self, surface):
        self.s.fill(transparent)
        Group.draw(self, self.s)
        surface.blit(self.s, (0, 0))


class RainSplash(Sprite):
    def __init__(self, area):
        self.max_radius = 200
        self.log = logging.getLogger(self.__class__.__name__)
        self.area = area
        Sprite.__init__(self, area.width, area.height)
        self.rect = self.image.get_rect()

        self.radius = 0
        self.splash()

    def update(self):
        self.radius = (self.radius + 3)
        if self.radius >= self.max_radius:
            self.splash()

        self.image.fill(white)
        c = hls_to_rgb(210,  (1+sin(self.radius/20))*49, 55)
        for i in range(self.radius):
            c = hls_to_rgb(210,  (1+sin(i/20))*49, 55)
            pygame.draw.circle(self.image, c, (self.position[0], self.position[1]), self.radius-i)

        self.image.set_alpha(255-(255*self.radius / self.max_radius))

        #pygame.draw.circle(self.image, c, (200,200), self.radius)

    def splash(self):
        self.radius = 0
        self.position = (randint(0, self.area.width), randint(0, self.area.height))


        # draw expanding blue/white circle with alpha
        #self.height = 1/self.radius


class Thunderstorm(Group):
    def __init__(self, size, ceiling):
        self.log = logging.getLogger(self.__class__.__name__)
        Group.__init__(self)
        self.s = pygame.Surface(size)
        self.s.set_colorkey(white)

class Lightning(Sprite):
    def __init__(self, ):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self)

class SheetLighting(Lightning):
    color = (255, 36, 251)

class ForkLighting(Lightning):
    color = (246, 255, 71)

class Splash(Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self)

class Wave(Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self)

class Bouy(Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self)
        self.colour = choice('red', 'green')


class Bird(Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self)

class ForestCanopey(Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self)

class Aurora(Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self)

class Constallation(Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self)

class HSMoon(Sprite):
    #uri = 'Resources/hackspace_logo_large.svg'

    """
    164.201, 327.203
    215.657, 275.746




    """
    def __init__(self, x = 300, y=300, r=150):
        Sprite.__init__(self, x,y)
        # Call the parent class (Sprite) constructor
        self.x, self.y, self.radius = x,y,r
        self.hlogo = pygame.image.load(os.path.join('Resources','hackspace_logo_large.png'))

        self.hlogo = pygame.transform.scale(self.hlogo, (200, 200))
        self.image.blit(self.hlogo, (0,0))
        #self.logo = pygame.image.load(self.uri)

    def draw(self, screen):
        screen.blit(self.image, (315,180))

        pass



## todo
#test pattern
#single pixel
#50:50
#




