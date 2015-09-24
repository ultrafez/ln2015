__author__ = 'ajtag'
import pygame
import random 
from random import randint
import colorsys
from math import pi, sin, cos
import math
import os.path
import csv
import collections

import logging

white = 255, 255, 255
transparent = 255,255,255,0
black = 0, 0, 0


def hls_to_rgb(hue, lightness, saturation):
    '''
    :param hue: 0-360
    :param lightness:  0-100
    :param saturation:  0-100
    :return: list
    '''
    return [i *255 for i in colorsys.hls_to_rgb(hue/360, lightness/100, saturation/100)]


class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.log = logging.getLogger(self.__class__.__name__)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((x, y))
        self.image.set_colorkey(white)
        self.image.fill(white)
        self.log.debug('##init##')


class Group(pygame.sprite.Group):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        pygame.sprite.Group.__init__(self)


Lamp = collections.namedtuple("Lamp", ["x", "y"])

class Ceiling:
    def __init__(self, filename):
        self.lamps = []
        self.readlamps(filename)

    def readlamps(self, filename):
        #Generate array of lights fixture locations
        f = open(filename)
        csv_f = csv.DictReader(f )
        for row in csv_f:
            #Adjusted XY coords -1 as Madrix counts from 1
            self.lamps.append(Lamp(int(row['X']) - 1 ,int(row['Y']) - 1))


class Star(Sprite):
    #TODO: shooting star

    def __init__(self, lamp):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self, 1, 1)

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.rect = (lamp.x, lamp.y, 1, 1)

        self.color = white
        self.rand_color()

        self.lamp = lamp

        self.log.debug('created star at {},{}'.format(lamp.x, lamp.y))

    def rand_color(self):
        self.color = hls_to_rgb(randint(40, 60), randint(20, 100), randint(80, 100))

    def update(self):
        self.image.set_at((0,0),self.color)


class StarrySky(Group):
    def __init__(self, size, ceiling):
        self.log = logging.getLogger(self.__class__.__name__)
        Group.__init__(self)
        self.lamps = ceiling.lamps
        self.alpha = 0
        self.dalpha = 2

        self.s = pygame.Surface(size)
        self.s.set_colorkey(white)

    def update(self):
        self.alpha = min(255, max(0, self.alpha + self.dalpha))
        self.s.set_alpha(self.alpha)

        r = random.randrange(0, 100)
        if r < 15:
            self.log.debug('add star')
            lamp = random.choice(self.lamps)
            self.add(Star(lamp))

        elif r == 99:
            self.log.warn('add Shooting Star')
        Group.update(self)

    def draw(self, surface):
        self.s.fill(white)
        Group.draw(self, self.s)
        surface.blit(self.s, (0, 0))

    def end(self):
        self.log.debug('Fade Stars Out')
        self.dalpha = -5
        pass


class RisingSun(Sprite):
    chordlengths = []

    def __init__(self,x,y, path,  max_radius=200, min_radius=50, speed = 4):
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
        self.rate = speed
        self.time = 0
        self.log.debug('initing sun')

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

    def update(self):
        self.time += 1
        self.set_height(min(1, 1000.0 / self.time*self.rate))

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
            self.log.debug('adding new cloud {}, {}, angry:{}'.format(self.starteast, self.gowest, self.angryness))
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
        self.log.debug('Fade clouds Out')

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
        self.drop_frequency = 23
        self.count = 0
        self.s.set_alpha(100)
        self.alpha = 100
        self.active_drops = 0

    def update(self):
        if self.count == 0:
            self.count = self.drop_frequency
            if self.active_drops < 5:
                self.active_drops += 1
        self.count -= 1
        if len(self) < self.active_drops:
            (w, h) = self.s.get_size()
            self.add(RainSplash(random.randrange(w), random.randrange(h), 60))
        Group.update(self)

    def draw(self, surface):
        self.s.fill(transparent)
        Group.draw(self, self.s)
        surface.blit(self.s, (0, 0))


class RainSplash(Sprite):
    def __init__(self, x, y, size):
        self.max_radius = size // 2
        self.log = logging.getLogger(self.__class__.__name__)
        Sprite.__init__(self, size, size)
        self.rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
        self.radius = 0

    def update(self):
        self.radius = (self.radius + 2)
        if self.radius >= self.max_radius:
            self.kill()
            return

        self.image.fill(white)
        c = hls_to_rgb(210,  (1+sin(self.radius/20))*49, 55)
        for i in range(self.radius):
            c = hls_to_rgb(210,  (1+sin(i/20))*49, 55)
            pygame.draw.circle(self.image, c, (self.max_radius, self.max_radius), self.radius-i)

        self.image.set_alpha(255-(255*self.radius / self.max_radius))

        #pygame.draw.circle(self.image, c, (200,200), self.radius)

        # draw expanding blue/white circle with alpha
        #self.height = 1/self.radius


class Thunderstorm(Group):
    def __init__(self, size, ceiling):
        self.log = logging.getLogger(self.__class__.__name__)
        Group.__init__(self)
        self.s = pygame.Surface(size)
        self.s.set_colorkey(white)

class Lightning(Sprite):
    def __init__(self, rect):
        # Call the parent class (Sprite) constructor
        self.rect = rect
        Sprite.__init__(self, rect.width, rect.height)
        self.potential = 800
        self.breakdown_potential = 800
        self.image.set_colorkey(white)

    def update(self):
        self.image.fill(white)

        self.potential += random.randint(0, 30)
        if self.potential > self.breakdown_potential:
            chance = random.randrange(100)
            power = random.randint(self.potential, 3 * self.potential)

            if chance < 80:
                self.flash( power/ (3 * self.potential) )
            self.potential = max(0, self.potential - power)


    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def flash(self, power):
        """
            draw a flash to the surface
        """
        pass

class SheetLighting(Lightning):
    color = (255, 36, 251)
    def flash(self, power):
        self.log.info('flash power {}'.format(power*255))
        self.image.set_alpha(power*255)
        pygame.draw.circle(self.image, self.color, (int(self.rect.width/2), int(self.rect.height/2)), int(self.rect.height/2))


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
        self.colour = random.choice('red', 'green')
        def update(self):
            self.image




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



