__author__ = 'ajtag'
import random
from random import randint
import colorsys
from math import pi, sin
import math
import os.path
import logging
from TrinRoofPlayer.Renderer import ceiling
import pygame
import numpy as np

white = 255, 255, 255
transparent = 255, 255, 255, 0
black = 0, 0, 0


def hls_to_rgb(hue, lightness, saturation):
    """
    :param hue: 0-360
    :param lightness:  0-100
    :param saturation:  0-100
    :return: list
    """
    return [i * 255 for i in colorsys.hls_to_rgb(hue / 360.0, lightness / 100.0, saturation / 100.0)]


def hlsa_to_rgba(hue, lightness, saturation, alpha):
    """
    :param hue: 0-360
    :param lightness:  0-100
    :param saturation:  0-100
    :return: list
    """
    rgb = colorsys.hls_to_rgb(hue / 360.0, lightness / 100.0, saturation / 100.0)

    rgba = [0,0,0,alpha]
    for n, i in enumerate(rgb):
        rgba[n] = i * 255
    return rgba


class Sprite(pygame.sprite.Sprite):
    def __init__(self, x=None, y=None, surface_flags=0):
        self.log = logging.getLogger(self.__class__.__name__)
        super().__init__()
        if x is not None:
            self.image = pygame.Surface((abs(x), abs(y)), surface_flags)
            self.image.set_colorkey(white)
            self.image.fill(white)
        self.log.debug('##init##')


class Group(pygame.sprite.Group):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        super().__init__()

    def end(self):
        raise StopIteration

class skybox(Sprite):
    def __init__(self, size):
        super(self).__init__(self)
        self.rect = pygame.Rect((0,0), size)
        self.colour = black

    def update_color(self, color):
        self.color = color

    def update(self):
        self.image.fill(self.color)

class Star(Sprite):
    # TODO: shooting star

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
        self.image.set_at((0, 0), self.color)
        self.rand_color()


class StarrySky(Group):
    def __init__(self, size):
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

    def fade(self):
        self.log.debug('Fade Stars Out')
        self.dalpha = -5
        pass


class RisingSun(Sprite):
    def __init__(self, start, end, size, duration, fade):
        super().__init__(size * 2, size * 2)

        self.start = start
        self.move_x = end[0] - start[0]
        self.move_y = end[1] - start[1]
        self.size = size
        self.rect = self.image.get_rect()
        self.duration = duration
        self.fade = 1.0 / fade

        self.time = 0.0
        self.alpha = 1.0
        self.log.debug('initing sun')
        self.render()

    def render(self):
        p = pygame.PixelArray(self.image)
        d2 = self.size * self.size
        for x in range(p.shape[0]):
            for y in range(p.shape[1]):
                dx = self.size - x
                dy = self.size - y
                dist = dx * dx + dy * dy
                if dist < d2:
                    color = (255, 255 - int(255 * dist / d2), 0)
                    p[x, y] = color

    def update(self):
        if self.time < 1.0:
            self.time += 1.0 / self.duration
            x = self.start[0] + self.time * self.move_x
            y = self.start[1] + self.time * self.move_y
            self.rect.center = (x, y)
        else:
            self.time = 1.0
            self.alpha -= self.fade
            if self.alpha < 0.0:
                raise StopIteration
            self.image.set_alpha(255 * self.alpha)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


def height_color(height):
    # height = 0:pi * 4/6
    height_hue = int(sin(height) * 40 * 6 / 4 / pi)
    height_lum = int(sin(height) * 6 / 4 / pi * 50)

    height_hue = (350 + randint(height_hue, (height_hue + 20))) % 360
    height_lum = 40 + randint(height_lum, height_lum + 10)

    return hls_to_rgb(height_hue, height_lum, randint(90, 100))


class Cloud(Sprite):
    def __init__(self, max_x, y, size):
        super().__init__()
        self.x = float(-size)
        self.y = y
        self.size = size
        self.bitmap = np.zeros((size + 1, size))
        self.max_x = max_x
        for x in range(size):
            for y in range(size):
                self.bitmap[x, y] = random.random()

    def update(self):
        self.x += 0.2
        if self.x > self.max_x:
            self.kill()

    def draw(self, alpha):
        """Anti-aliased x transparency mask"""
        x_start = int(self.x)
        if self.x < 0:
            x_start -= 1
        x_offset = self.x - x_start
        for y in range(self.size):
            py = y + self.y
            if py < 0 or py >= alpha.shape[1]:
                continue
            for x in range(self.size + 1):
                px = x_start + x
                if px < 0 or px >= alpha.shape[0]:
                    continue
                a = self.bitmap[x - 1, y]
                b = self.bitmap[x, y]
                val = int(255 * (b + (a - b) * x_offset))
                orig = alpha[px, py]
                alpha[px, py] = min(orig + val, 255)


class Clouds(Group):
    def __init__(self, size, cloud_size, initial_prob, final_prob, ramp_duration):
        super().__init__()
        self.cloud_size = cloud_size
        self.s = pygame.Surface(size, flags = pygame.SRCALPHA)
        self.color = (255, 255, 255, 0)
        self.max_x = size[0]
        self.max_y = size[1] - cloud_size
        self.time = 0
        self.initial_prob = initial_prob
        self.final_prob = final_prob
        self.ramp_duration = ramp_duration
        self.grey_time = None
        self.black_time = None

    def grey(self, duration):
        self.grey_time = duration
        self.time = 0

    def update(self):
        if self.grey is not None:
            if self.time > self.ramp_duration:
                p = self.final_prob
            else:
                a = self.initial_prob
                b = self.final_prob
                p = a + (b - a) * self.time / self.ramp_duration
            while True:
                p -= random.random()
                if p < 0.0:
                    break
                self.add(Cloud(self.max_x, random.randrange(self.max_y), self.cloud_size))
        self.time += 1
        super().update()

    def draw(self, surface):
        skip = False
        if self.black_time is not None:
            if self.time > self.grey_time:
                raise StopIteration
            p = self.time / self.grey_time
            shade = int(128 * (1.0 - p))
            surface.fill((shade, shade, shade, 255))
            return
        if self.grey_time is not None:
            if self.time >= self.grey_time:
                surface.fill((128, 128, 128, 255))
                return
            p = self.time / self.grey_time
            alpha = int(255 * p)
            shade = 255 - alpha // 2
            self.color = (shade, shade, shade, alpha)
        self.s.fill(self.color)
        a = pygame.surfarray.pixels_alpha(self.s)
        for cloud in self:
            cloud.draw(a)
        del a
        surface.blit(self.s, (0, 0))

    def end(self, duration):
        self.black_time = duration
        self.time = 0


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
        # c = hls_to_rgb(210, (1 + sin(self.radius / 20)) * 49, 55)
        for i in range(self.radius):
            c = hls_to_rgb(210, (1 + sin(i / 20)) * 49, 55)
            pygame.draw.circle(self.image, c, (self.max_radius, self.max_radius), self.radius - i)

        self.image.set_alpha(255 - (255 * self.radius / self.max_radius))

        # pygame.draw.circle(self.image, c, (200,200), self.radius)
        # draw expanding blue/white circle with alpha
        # self.height = 1/self.radius


class Thunderstorm(Group):
    def __init__(self):

        self.log = logging.getLogger(self.__class__.__name__)
        Group.__init__(self)

    def add_sheet(self, r):
        self.add(SheetLighting(r))

    def add_fork(self, size, start, end):
        self.add(ForkLighting(size, start, end))


class Lightning(Sprite):
    def __init__(self, rect):
        # Call the parent class (Sprite) constructor
        self.rect = rect
        Sprite.__init__(self, rect.width, rect.height)
        self.potential = 800
        self.breakdown_potential = 800
        self.image.set_colorkey(white)
        self.flashing = False
        self.power = 0

    def update(self):
        if self.flashing:
            self.flash(self.power)
            return

        self.potential += random.randint(0, 30)
        if self.potential > self.breakdown_potential:
            chance = random.randrange(100)
            power = random.randint(self.potential, 3 * self.potential)

            if chance < 80:
                self.flash(power / (3 * self.potential))
            self.potential = max(0, self.potential - power)
        else:
           self.image.fill(white)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def flash(self, power):
        """
            draw a flash to the surface
        """
        self.flashing = False
        pass


class SheetLighting(Lightning):
    color = (255, 36, 251)

    def flash(self, power):
        self.log.info('flash power {}'.format(power * 255))
        self.image.set_alpha(power * 255)
        self.image.fill(self.color)
        self.flashing = False


class ForkLighting(Lightning):
    color = (246, 255, 71)

    def __init__(self, size, start, end):
            print(start, end)
            self.start = pygame.math.Vector2(start)
            self.end = pygame.math.Vector2(end)
            self.ionised = [self.start]
            self.speed = 3
            super().__init__(pygame.Rect((0,0), size))

    def flash(self, power):
        self.flashing = True
        for i in range(random.randrange(3, 8)):
            last = self.ionised[-1]
            togo = self.end - last
            lp = togo.as_polar()
            if lp[0] < 2:
                self.flashing = False
                self.image.fill(white)
                self.ionised = [self.ionised[0]]
                return
            togo.from_polar((1.5, random.triangular(-180, 180) + lp[1]))
            n = last + togo
            self.ionised.append(n)
            pygame.draw.line(self.image, self.color, last, n, 2)


class Bouy(Sprite):
    def __init__(self, location):
        Sprite.__init__(self, 19, 19, pygame.SRCALPHA)
        self.rect = pygame.Rect(location, (19, 19))
        self.colour = random.choice( (350.0, 30.0, 60.0, 90.0, 230.0) )
        self.ticks = 0
        self.flash_age = 20
        self.flash_speed = 0.3

    def flash(self):
        self.flash_age = self.flash_speed

    def update(self):
        self.image.fill(transparent)
        pygame.draw.rect(self.image, (0x30, 0x30, 0x30, 0x30), pygame.Rect(8, 8, 3, 3), 0)  # draw gray bouy
        if self.flash_age < 9:
            for i in range(19):
                for j in range(19):
                    l = pygame.math.Vector2(9-i, 9-j).length()
                    if l > self.flash_age:
                        self.image.set_at((i, j), transparent)
                    else:
                        o = ((9-self.flash_age)/9) * (l/self.flash_age)
                        c = hlsa_to_rgba(self.colour, 40.0, 100.0, o*255)
                        self.image.set_at((i, j), c)

                    if i == 9 and j == 9:
                        c = hlsa_to_rgba(self.colour, (100*((9-self.flash_age)/9)), 100.0, 255)
                        self.image.set_at((i, j), c)

        # self.image
        self.flash_age += self.flash_speed

    def end(self):
        self.kill()

class Bird(Sprite):
    def __init__(self, rect):
        # Call the parent class (Sprite) constructor
        self.ticks = 0
        self.active_frame = 0
        self.rect = rect
        self.frames = []
        self.action = 'bob'
        self.next_action = 'bob'
        self.frame_loader()

        self.actions = {'bob':(0, ),
                        'takeoff': (1, 2, 3, 4, 5, 6, 32),
                        'flap': ( 33, 34, 35, 36, 37, 38, 39, 40, 41, 42),
                        'rotate_camera': (12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30),
                        'soar': (31,)
                        }

        Sprite.__init__(self, self.rect.width, self.rect.height)

    def set_action(self, action):
        self.next_action = action

    def frame_loader(self, frameid=0):
        max_x = 0
        max_y = 0
        try:
            while True:
                fn = os.path.join('Resources','bird', 'bird_{}.png'.format(frameid))
                if not os.path.isfile(fn):
                    raise LookupError
                frame = pygame.image.load(fn)
                max_x = max(max_x, frame.get_rect().width)
                max_y = max(max_y, frame.get_rect().height)
                self.frames.append(frame)
                frameid += 1
        except LookupError:
            pass
        if len(self.frames) == 0:
            raise StopIteration

        self.rect.size = (max_x, max_y)

    def update(self):

        if self.ticks == 100:
            self.set_action('takeoff')
            self.log.info('takeoff')


        if self.ticks == 500:
            self.log.info('rotate_camera')
            self.set_action('rotate_camera')


        if self.ticks == 2500:
            raise StopIteration

        if self.ticks % 5 == 0:
            self.active_frame += 1
            self.active_frame = self.active_frame % len(self.actions[self.action])
            if self.active_frame == 0:
                self.action = self.next_action

        self.image.fill((255, 255, 255, 128,))
        self.image.blit(self.frames[self.actions[self.action][self.active_frame]], (0, 0))



        if self.action == 'takeoff':
            self.set_action('flap')

        if self.action == 'rotate_camera':
            self.set_action('soar')

        self.ticks += 1


class Aurora(Sprite):
    def __init__(self, x, y):
        colors = [hls_to_rgb(120, 21, 100), hls_to_rgb(300, 21, 100)]
        # Call the parent class (Sprite) constructor
        self.line = (10, 4, 6, 2, 8, 12, 6)
        Sprite.__init__(self, x, y);

        self.image = pygame.draw.arc()



    def update(self):
        pass


class Constellation(Sprite):
    def __init__(self, x, y):
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self, x, y)


class HSMoon(Sprite):
    # uri = 'Resources/hackspace_logo_large.svg'

    """
    164.201, 327.203
    215.657, 275.746




    """

    def __init__(self, x=300, y=300, r=150, angle=0, angle_delta=-3):
        Sprite.__init__(self, r*2, r*2)
        self.rect = pygame.Rect(x, y, r*2, r*2)
        self.angle = angle
        self.dangle = angle_delta
        # Call the parent class (Sprite) constructor
        self.x, self.y, self.radius = x, y, r
        self.hlogo = pygame.image.load(os.path.join('Resources', 'hackspace_logo_large.png'))
        self.scale_factor = r * 2 / self.hlogo.get_height()

        #self.hlogo = pygame.transform.scale(self.hlogo, (200, 200))
        #self.image.blit(self.hlogo, (0, 0))
        # self.logo = pygame.image.load(self.uri)

    def update(self):
        self.image.fill((255,0,0))
        self.angle += self.dangle
        self.image = pygame.transform.rotozoom(self.hlogo, self.angle, self.scale_factor)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def end(self):
        raise StopIteration


def pythagoras(vector):
    return math.sqrt(vector[0] * vector[0] + vector[1] * vector[1])


class Wave(Sprite):
    def __init__(self, direction, size):
        super().__init__()
        self.direction = direction
        speed = pythagoras(direction)
        self.norm = (direction[1] / speed, -direction[0] / speed)
        self.max_x = size[0]
        self.max_y = size[1]
        if direction[0] > 0.0:
            start_x = 0.0
        else:
            start_x = self.max_x
        if direction[1] > 0.0:
            start_y = 0.0
        else:
            start_y = self.max_y
        self.pos = (start_x, start_y)

    def update(self, width):
        x = self.pos[0] + self.direction[0]
        y = self.pos[1] + self.direction[1]
        self.pos = (x, y)
        d = self.distance((0, 0))
        d = min(d, self.distance((0, self.max_y)))
        d = min(d, self.distance((self.max_x, self.max_y)))
        d = min(d, self.distance((self.max_x, 0)))
        if d > width * 2.0 + 1.0:
            self.kill()

    def distance(self, point):
        # for line X = A + tN, the distance to point P is
        # (A - P) - ((A - P).N)N 
        ap_x = self.pos[0] - point[0]
        ap_y = self.pos[1] - point[1]
        dot = ap_x * self.norm[0] + ap_y * self.norm[1]
        perp = (ap_x - dot * self.norm[0], ap_y - dot * self.norm[1])
        dist = pythagoras(perp)
        # Set sign based on which side of the line we are on
        dot2 = perp[0] * self.norm[1] - perp[1] * self.norm[0]
        if dot2 < 0:
            return dist
        else:
            return -dist

class Sea(Group):
    def __init__(self, size, num_waves, width):
        super().__init__()
        self.s = pygame.Surface(size, flags = pygame.SRCALPHA)
        self.num_waves = num_waves
        self.width = width
        self.dw = 0.0
        self.new_width = width
        self.new_timer = 0
        self.size = size

    def change(self, num_waves, width, time):
        self.dw = (width - self.width) / time
        self.new_width = width
        self.num_waves = num_waves
        self.new_timer = min(self.new_timer, self.size[0] // num_waves)

    def add_wave(self):
        r = random.random()
        self.add(Wave((random.choice((r, -r)), random.choice((r - 1.0, 1.0 - r))), self.size))

    def end(self):
        self.num_waves = 0

    def update(self):
        if self.num_waves == 0 and len(self) == 0:
            raise StopIteration
        if (self.dw > 0.0 and self.width < self.new_width) \
                or (self.dw < 0.0 and self.width > self.new_width):
            self.width += self.dw

        if self.new_timer > 0:
            self.new_timer -= 1

        if len(self) < self.num_waves and self.new_timer == 0:
            self.add_wave()
            self.new_timer = self.size[0] // self.num_waves

        for w in self:
            w.update(self.width)

    def draw(self, surface):
        if len(self) == 0:
            return
        self.s.fill(transparent)
        a = pygame.PixelArray(self.s)
        for lamp in ceiling.lamps:
                x = lamp.x
                y = lamp.y
        #for x in range(self.size[0]):
        #    for y in range(self.size[1]):
                close = self.width * 2.0 + 1.0
                for obj in self:
                    dist = obj.distance((x, y))
                    if dist > 0.0 and dist < close:
                        close = dist
                color = transparent
                if close > 0.0:
                    if close <= 1.0:
                        p = int(255 * close)
                        color = (255, 255, 255, p)
                    else:
                        close = (close - 1.0) / self.width
                        if close < 1.0:
                            p = int(255 * (1.0 - close))
                            color = (p, p, 255, 255)
                        elif close < 2.0:
                            p = int(255 * (2.0 - close))
                            color = (0, 0, 255, p)
                a[x, y] = color
        del a
        surface.blit(self.s, (0, 0))
