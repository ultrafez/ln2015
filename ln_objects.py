__author__ = 'ajtag'
import pygame
from random import randint, choice
import colorsys
import numpy as np
import xml.etree.ElementTree as ET
from numpy import pi, sin, cos


white = 255, 255, 255



def hls_to_rgb(hue, lightness, saturation):
    return np.array(colorsys.hls_to_rgb(hue/360, lightness/100, saturation/100)) * 255


class Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((x, y))
        self.image.set_colorkey(white)
        self.image.fill(white)


class Lamp:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Ceiling:
    lamps = []
    mask = None

    def __init__(self, x, y):
        tree = ET.parse('/home/ajtag/workspace/ln2015/LS-TRIN-0023 East Mall.svg')

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
        mask = pygame.Surface((x, y))

        #print(mnlx, mxlx, mnly, mxly)
        mnlx -= 5
        mxlx += 5
        mnly -= 5
        mxly += 5
        for lamp in tmplamps:
            self.lamps.append(
                Lamp((lamp[0] - mnlx)/(mxlx - mnlx) * x,(lamp[1] - mnly)/(mxly - mnly) * y))
            pos = pygame.Rect(
                (lamp[0] - mnlx)/(mxlx - mnlx) * x,(lamp[1] - mnly)/(mxly - mnly) * y,
                2, 2)
            pygame.draw.rect(mask, white, pos, 0)

        mask.set_colorkey(white)
        self.mask = (mask)

black = 0, 0, 0

class Star(Sprite):
    #TODO: shooting star

    def __init__(self, lamp, starsize=5):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self, 2*starsize, 2*starsize)
        self.starsize = starsize

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.rect = (lamp.x, lamp.y, 2*starsize, 2*starsize)

        self.color = white
        self.rand_color()

        self.lamp = lamp

    def rand_color(self):
        self.color = hls_to_rgb(randint(40, 60), randint(20, 100), randint(80, 100))

    def update(self):
        pygame.draw.circle(self.image, self.color, (self.starsize, self.starsize), self.starsize)


class StarrySky(pygame.sprite.Group):

    def __init__(self, size, ceiling):
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
            print('add star')
            l = randint(0, len(self.ceiling.lamps)+1)
            self.add(Star(self.ceiling.lamps[l]))
        elif r == 99:
            print('add Shooting Star')
        pygame.sprite.Group.update(self)

    def draw(self, surface):
        self.s.fill(white)
        pygame.sprite.Group.draw(self, self.s)
        surface.blit(self.s, (0, 0))

    def end(self):
        self.dalpha = -5
        pass


class RisingSun(pygame.sprite.Sprite):
    chordlengths = []

    def __init__(self, x, y, radius):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self, radius*2, radius*2)
        ## init rect
        self.x, self.y = x, y
        self.radius = radius
        self.update_rect()

        # init image to tranparent
        self.height = 0
        self.update_chords()

    def set_height(self, time):
        self.height = time/6 * pi
        self.y -= 0.5
        self.x += 0.2

        self.set_radius(self.radius - 1)

        self.update_chords()

    def update_chords(self):
        #chordlengths
        self.chordlengths = [2 * np.power( ((self.radius * self.radius) - (d * d)), 0.5) for d in range(0, self.radius)]

    def set_radius(self, r):
        self.radius = max( r, 20)
        self.update_chords()

    def update_rect(self):
        self.rect = (self.x, self.y, self.radius*2, self.radius*2)

    def move_dxdy(self, dx, dy):
        self.x += dx
        self.y += dy
        self.update_rect()

    def move_abs(self, x, y):
        self.x = x
        self.y = y
        self.update_rect()

    def draw(self, surface):

        self.image.fill(black)
        #print(self.chordlengths)
        for n, d in enumerate(self.chordlengths):
            c = height_color(self.height)
            pygame.draw.aaline(self.image, c, (self.radius - d/2 ,(self.radius + n)), (((2*self.radius) - (self.radius-d/2)), (self.radius + n)), True)
            c = height_color(self.height)
            pygame.draw.aaline(self.image, c, (self.radius - d/2 ,(self.radius - n)), (((2*self.radius) - (self.radius-d/2)), (self.radius - n)), True)
        surface.blit(self.image, (self.x, self.y))

def height_color(height):
        # height = 0:pi * 4/6
        height_hue = int(np.sin(height) * 40 * 6 / 4/ pi)
        height_lum = int(np.sin(height) * 6/4/pi*50)

        height_hue = (350 + randint(height_hue, (height_hue+20))) % 360
        height_lum = 40 + randint(height_lum, height_lum+10)

        return hls_to_rgb(height_hue, height_lum, randint(90, 100))

class Cloud(pygame.sprite.Sprite):
    def __init__(self, angryness, radius):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.angryness = angryness
        self.radius = radius

class Lightning(pygame.sprite.Sprite):
    def __init__(self, ):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.colour = None


class SheetLighting(Lightning):
    pass

class ForkLighting(Lightning):
    pass



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





