__author__ = 'ajtag'
import colorsys
from math import pi, sin
import math
import os.path
import logging
from TrinRoofPlayer.Renderer import ceiling, get_fps, new_random
from TrinRoofPlayer.Constants import *
import pygame
from pygame.math import Vector2
import numpy as np

#To change random seed add self.rand.seed(1) to innit funciton of group find a number that works!

white = 255, 255, 255
transparent = 255, 255, 255, 0
black = 0, 0, 0


def hls_to_rgb(hue, lightness, saturation):
    """
    :param hue: 0-360
    :param lightness:  0-100
    :param saturation:  0-100
    :return: list(int)
    """
    return [int(i * 255) for i in colorsys.hls_to_rgb(hue / 360.0, lightness / 100.0, saturation / 100.0)]


def hlsa_to_rgba(hue, lightness, saturation, alpha):
    """
    :param hue: 0-360
    :param lightness:  0-100
    :param saturation:  0-100
    :return: list(int)
    """
    rgb = colorsys.hls_to_rgb(hue / 360.0, lightness / 100.0, saturation / 100.0)

    rgba = [0,0,0,alpha]
    for n, i in enumerate(rgb):
        rgba[n] = int(i * 255)
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
        self.ticks = 0


class Group(pygame.sprite.Group):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        super().__init__()
        self.rand = new_random(self.__class__.__name__)

    def end(self):
        raise StopIteration

class Star(Sprite):
    def __init__(self, lamp, duration, color):
        super().__init__()
        self.color = color
        self.lamp = lamp
        self.time = -1.0
        self.rate = 1.0 / (get_fps() * duration)

    def update(self):
        self.time += self.rate
        if self.time >= 1.0:
            self.kill()

    def draw(self, surface, fade):
        bright = (1.0 - abs(self.time)) * fade
        color = tuple(int(c * bright) for c in self.color)
        pos = (self.lamp.x, self.lamp.y)
        surface.set_at(pos, color)

class StarrySky(Group):
    def __init__(self, max_stars, ramp_time, min_time, max_time):
        super().__init__()
        self.lamps = ceiling.lamps
        self.ramp_rate = max_stars / (get_fps() * ramp_time)
        self.num_stars = 1.0
        self.max_stars = max_stars
        self.fade = 1.0
        self.fade_rate = 0.0
        self.min_time = min_time
        self.max_time = max_time

    def add_star(self):
        lamp = self.rand.choice(self.lamps)
        color = hls_to_rgb(self.rand.randint(40, 60), self.rand.randint(20, 100), self.rand.randint(80, 100))
        self.add(Star(lamp, self.rand.uniform(self.min_time, self.max_time), color))

    def update(self):
        self.fade += self.fade_rate
        if self.fade <= 0.0:
            raise StopIteration
        if self.num_stars < self.max_stars:
            self.num_stars +=  self.ramp_rate
        elif self.num_stars > self.max_stars:
            self.num_stars = self.max_stars
        while len(self) < self.num_stars:
            self.add_star()
        super().update()

    def draw(self, surface):
        for star in self:
            star.draw(surface, self.fade)

    def end(self, fade_time):
        self.fade_rate = -1.0 / (get_fps() * fade_time)


class MoveableThing(Group):
    def __init__(self, pos, size, fade_duration):
        super().__init__()
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.dx = 0.0
        self.dy = 0.0
        self.steps = 0
        self.size = size
        self.size_speed = 0

        if fade_duration is not None:
            self.fade = 0.0
            self.fade_speed = 1.0 / (get_fps() * fade_duration)
        else:
            self.fade = 1.0
            self.fade_speed = None

    def update(self):
        if self.steps > 0:
            self.steps -= 1
            self.x += self.dx
            self.y += self.dy
            self.size += self.size_speed
        if self.fade_speed is not None:
            self.fade += self.fade_speed
            if self.fade_speed > 0.0 and self.fade >= 1.0:
                self.fade = 1.0;
                self.fade_speed = None
            elif self.fade_speed < 0.0 and self.fade <= 0.0:
                raise StopIteration

    def move(self, newpos, newsize, duration = None):
        if duration is None:
            self.steps = 1
        else:
            self.steps = max(int(duration * get_fps()), 1)
        if newpos is None:
            self.dx = 0.0
            self.dy = 0.0
        else:
            self.dx = (newpos[0] - self.x) / self.steps
            self.dy = (newpos[1] - self.y) / self.steps
        if newsize is None:
            self.size_speed = 0
        else:
            self.size_speed = (newsize - self.size) / self.steps

    def end(self, fade_duration = None):
        if fade_duration is None:
            raise StopIteration
        else:
            self.fade_speed = -1.0 / (get_fps() * fade_duration)

class Sun(MoveableThing):
    def __init__(self, pos, size, ripple_height, ripple_count, ripple_speed, duration = None):
        super().__init__(pos, size, duration)
        self.s = pygame.Surface(MADRIX_SIZE, flags = pygame.SRCALPHA)
        self.ripple_speed = ripple_speed * math.pi * 2.0 / get_fps()
        self.ripple_distance = ripple_count * math.pi * 2.0
        self.ripple_height = ripple_height / 2.0
        self.ripple = 0.0

    def update(self):
        super().update()
        self.ripple += self.ripple_speed
        if self.ripple > math.pi * 2.0:
            self.ripple -= math.pi * 2.0

    def draw(self, surface):
        self.s.fill(transparent)
        a = pygame.PixelArray(self.s)
        left = max(int(self.x - self.size) - 1, 0)
        right = min(int(self.x + self.size) + 2, a.shape[0])
        top = max(int(self.y - self.size) - 1, 0)
        bottom = min(int(self.y + self.size) + 2, a.shape[1])
        for x in range(left, right):
            for y in range(top, bottom):
                dx = self.x - x
                dy = self.y - y
                dist = dx * dx + dy * dy
                dist = pythagoras((dx, dy))
                if dist <= self.size + 1:
                    height = max(1.0 - dist / self.size, 0.0)
                    ripple_pos = self.ripple + height * self.ripple_distance
                    height -= height * self.ripple_height * (sin(ripple_pos) + 1)
                    if dist <= self.size:
                        alpha = 255
                    else:
                        alpha = 255 * (self.size  + 1 - dist)
                    alpha = int(alpha * self.fade)
                    color = (255, int(255 * height), 0, alpha)
                    a[x, y] = color
        del a
        surface.blit(self.s, (0,0))

class Fog(Sprite):
    def __init__(self, color, duration = None):
        if duration is None:
            self.level = 1.0
            self.rate = None
        else:
            self.rate = 1.0 / (get_fps() * duration)
            self.level = 0.0
        self.s = pygame.Surface(MADRIX_SIZE)
        self.s.fill(color)

    def update(self):
        if self.rate is not None:
            self.level += self.rate
            if self.level > 1.0:
                self.level = 1.0
                self.rate = None
            if self.level <= 0.0:
                raise StopIteration

    def end(self, duration = None):
        if duration is None:
            raise StopIteration
        self.rate = -1.0 / (get_fps() * duration)

    def draw(self, surface):
        self.s.set_alpha(int(255 * self.level))
        surface.blit(self.s, (0,0))

class Cloud(Sprite):
    def __init__(self, max_x, y, size, rand):
        super().__init__()
        self.x = float(-size)
        self.y = y
        self.size = size
        self.bitmap = np.zeros((size + 1, size))
        self.max_x = max_x
        for x in range(size):
            for y in range(size):
                self.bitmap[x, y] = rand.random()

    def update(self):
        self.x += 0.2
        if self.x > self.max_x:
            self.kill()

    def draw(self, pixels, fade):
        """Anti-aliased x transparency mask"""
        x_start = int(self.x)
        if self.x < 0:
            x_start -= 1
        x_offset = self.x - x_start
        for y in range(self.size):
            py = y + self.y
            if py < 0 or py >= pixels.shape[1]:
                continue
            for x in range(self.size + 1):
                px = x_start + x
                if px < 0 or px >= pixels.shape[0]:
                    continue
                v1 = self.bitmap[x - 1, y]
                v2 = self.bitmap[x, y]
                val = v2 + (v1 - v2) * x_offset
                new_alpha = int(255 * val * fade)
                alpha = pixels[px, py]
                alpha = max(alpha, new_alpha)
                pixels[px, py] = alpha


class Clouds(Group):
    CLOUD_NORMAL = 1
    CLOUD_GREY = 2
    CLOUD_BLACK = 3
    def __init__(self, size, cloud_size, initial_prob, final_prob, ramp_duration):
        super().__init__()
        self.cloud_size = cloud_size
        self.s = pygame.Surface(size, flags = pygame.SRCALPHA)
        self.color = (255, 255, 255, 0)
        self.max_x = size[0]
        self.max_y = size[1] - cloud_size
        self.initial_prob = initial_prob
        self.final_prob = final_prob
        self.ramp_speed = None
        self.time = None
        self.set_ramp(ramp_duration)
        self.phase = self.CLOUD_NORMAL
        self.dirtyness = 0.0

    def set_ramp(self, duration):
        self.ramp_speed = 1.0 / (get_fps() * duration)
        self.time = 0.0

    def grey(self, whiteness, duration):
        self.set_ramp(duration)
        self.dirtyness = 1.0 - whiteness
        self.phase = self.CLOUD_GREY

    def update(self):
        if self.time >= 1.0:
            p = self.final_prob
        else:
            a = self.initial_prob
            b = self.final_prob
            p = a + (b - a) * self.time
        while True:
            p -= self.rand.random()
            if p < 0.0:
                break
            self.add(Cloud(self.max_x, self.rand.randrange(self.max_y), self.cloud_size, self.rand))
        self.time += self.ramp_speed
        super().update()

    def draw(self, surface):
        fade = 1.0
        shade = int(255 - 255 * self.dirtyness)
        if self.phase == self.CLOUD_BLACK:
            if self.time > 1.0:
                raise StopIteration
            fade = 1.0 - self.time
        if self.phase == self.CLOUD_GREY:
            if self.time < 1.0:
                shade = int(255  - 255 * self.dirtyness * self.time)
        self.s.fill((shade, shade, shade, 0))
        a = pygame.surfarray.pixels_alpha(self.s)
        for cloud in self:
            cloud.draw(a, fade)
        del a
        surface.blit(self.s, (0, 0))

    def end(self, duration):
        self.set_ramp(duration)
        self.phase = self.CLOUD_BLACK


class Raindrops(Group):
    def __init__(self, drop_size, drop_duration, max_drops, ramp_time):
        super().__init__()
        self.num_drops = 1.0
        self.max_drops = max_drops
        self.ramp_rate = max_drops / (get_fps() * ramp_time)
        self.drop_size = drop_size
        self.drop_speed = drop_size / (get_fps() * drop_duration)

    def update(self):
        if self.ramp_rate > 0.0:
            if self.num_drops < self.max_drops:
                self.num_drops += self.ramp_rate
            else:
                self.num_drops = self.max_drops
                self.ramp_rate = 0
        else:
            self.num_drops += self.ramp_rate

        max_drops = int(self.num_drops / get_fps()) + 1
        missing = int(self.num_drops) - len(self)
        for _ in range(min(missing, max_drops)):
            lamp = self.rand.choice(ceiling.lamps)
            self.add(RainSplash(self.drop_size, self.drop_speed, lamp))
        super().update()
        if len(self) == 0 and self.num_drops <= 0:
            raise StopIteration

    def draw(self, surface):
        for drop in self:
            drop.draw(surface)

    def end(self, ramp_time = None):
        if ramp_time is not None:
            self.ramp_rate = -self.num_drops / (get_fps() * ramp_time)
        else:
            self.num_drops = 0


class RainSplash(Sprite):
    def __init__(self, max_r, speed, lamp):
        super().__init__()
        self.pos = (lamp.x, lamp.y)
        self.max_radius = max_r
        self.radius = 0
        self.speed = speed

    def update(self):

        self.radius += self.speed
        if self.radius >= self.max_radius:
            self.kill()
            return

    def draw(self, surface):
        color = (0, 0, 255, 255)
        pygame.draw.circle(surface, color, self.pos, int(self.radius))


class Thunderstorm(Group):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        Group.__init__(self)
        self.ticks = 0
        self.group_trigger = False
        self.log.info('started storm')
        self.named_groups = {}
        self.program = None
        self.next_program = None

    def add_group(self, groupname, sprite):
        if groupname not in self.named_groups:
            self.named_groups[groupname] = Group()
        self.named_groups[groupname].add(sprite)
        self.add(sprite)

    def del_group(self, groupname):
        if groupname in self.named_groups:
            for s in self.named_groups[groupname].sprites():
                s.kill()

    def big_hit(self):
        self.log.info('big_hit')

        self.add_group('big_hit_sheet', SheetLighting(pygame.Rect((0, 0), MADRIX_SIZE)))
        self.add_group('big_hit', ForkLighting(MADRIX_SIZE, (67, 55), (67, 0)))
        self.add_group('big_hit', ForkLighting(MADRIX_SIZE, (67, 55), (3, 44)))
        self.add_group('big_hit', ForkLighting(MADRIX_SIZE, (67, 55), (128, 45)))
        self.trigger_flash(None, pulse=2*get_fps())


    def incoming(self, duration):
        self.log.info('incoming')
        self.empty()
        self.add_group('outer', SheetLighting(pygame.Rect(   0, -70, 132, 70), Vector2(  0, 36), duration))
        self.add_group('outer', SheetLighting(pygame.Rect(-132,   0, 132, 70), Vector2( 51,  0), duration))
        self.add_group('outer', SheetLighting(pygame.Rect( 132,   0, 132, 70), Vector2(-52,  0), duration))


    def outgoing(self, duration):
        self.log.info('outgoing')
        self.empty()
        self.add_group('outer', SheetLighting(pygame.Rect(   0, -34, 132, 70), Vector2(  0, -36), duration))
        self.add_group('outer', SheetLighting(pygame.Rect(-81,   0, 132, 70), Vector2( -51,  0), duration))
        self.add_group('outer', SheetLighting(pygame.Rect( 80,   0, 132, 70), Vector2(52,  0), duration))

    def set_group_trigger(self, state):
        self.group_trigger = state

    def trigger_flash(self, groupname=None, ignore=0, pulse=0):
        if self.group_trigger:
            if groupname in self.named_groups:
                g = self.named_groups[groupname]
            else:
                g = self
                for s in g.sprites():
                    if s != ignore:
                        s.charge()
                        s.flash(1, group_trigger=True, pulse=pulse)
            return

    def add_sheet(self, r, dx, duration):
        self.add(SheetLighting(r, dx, duration))

    def add_fork(self, size, start, end):
        self.add(ForkLighting(size, start, end))


class Lightning(Sprite):
    def __init__(self, rect):
        # Call the parent class (Sprite) constructor
        self.rect = rect
        Sprite.__init__(self, rect.width, rect.height, surface_flags=pygame.SRCALPHA)
        self.potential = 800
        self.breakdown_potential = 800
        self.flashing = False
        self.power = 0
        self.rand = new_random(self.__class__.__name__)
        self.ticks = 0
        self.pulse = 0
        self.pulse_duration = 0

    def update(self):
        if self.flashing:
            self.flash(self.power)
            return

        self.potential += self.rand.randint(0, 30)
        if self.potential > self.breakdown_potential:
            chance = self.rand.randrange(100)
            power = self.rand.randint(self.potential, 3 * self.potential)

            if chance < 80:
                self.flash(power / (3 * self.potential))
            self.potential = max(0, self.potential - power)
        else:
           self.image.fill(transparent)

        self.ticks += 1


    def flash(self, power):
        """
        """
        self.flashing = False
        pass # start lightning incoming

    def charge(self):
        self.potentential += self.potential

class SheetLighting(Lightning):
    def __init__(self, r, move=pygame.math.Vector2(0, 0), duration=0):
        super().__init__(r)
        self.color = (255, 36, 251)

        self.duration = duration * get_fps()
        self.move = move
        self.origin = self.rect.topleft

    def move_to(self, move, duration):
        self.move = move
        self.duration = duration * get_fps()
        self.ticks = 0

    def update(self):
        # move position if required
        if self.duration is not None and self.duration != 0:
            newpos = self.origin + (self.move * min(1, (self.ticks/self.duration)))
            self.rect.topleft = (round(newpos.x), round(newpos.y))
        super().update()

    def flash(self, power, group_trigger=False, pulse=False):
        if group_trigger:
            for g in self.groups():
                try:
                    g.trigger_flash(ignore=self, pulse=pulse)
                except AttributeError:
                    pass

        self.log.debug('flash power {}'.format(power * 255))
        self.image.set_alpha(power * 255)
        self.image.fill(self.color)
        self.flashing = False


class ForkLighting(Lightning):
    def __init__(self, size, start, end):
            self.color = [246, 255, 71, 255]
            self.start = pygame.math.Vector2(start)
            self.end = pygame.math.Vector2(end)
            self.ionised = [self.start]
            self.pulse = 0
            self.pulse_duration = 500
            super().__init__(pygame.Rect((0, 0), size), )

    def update(self):
        super().update()
        # render to image
        self.image.fill(transparent)
        start_segment = self.ionised[0]
        a_color = self.color

        if self.flashing or self.pulse < self.pulse_duration:
            for point in self.ionised[1:]:
                pygame.draw.line(self.image, self.color, start_segment, point, 1)
                if not self.flashing:
                    if self.pulse <= self.pulse_duration:
                        a_color[3] = 128 * sin(self.pulse/24) + 128
                        self.pulse += 1
                        pygame.draw.line(self.image, a_color, start_segment, point, 3)
                start_segment = point
        else:
            self.ionised = [self.ionised[0]]
            self.image.fill(transparent)

    def flash(self, power, group_trigger=False, pulse=None):
        self.flashing = True
        if pulse is not None:
            self.pulse_duration = pulse

        if self.rand.randint(0, 100) < 20:
            self.pulse_duration = 2 * get_fps()
            self.pulse = 0

        if group_trigger:
            for g in self.groups():
                try:
                    g.trigger_flash(ignore=self, pulse=self.pulse_duration)
                except AttributeError:
                    pass

        for i in range(self.rand.randrange(3, 8)):
            last = self.ionised[-1]
            togo = self.end - last
            lp = togo.as_polar()
            if lp[0] > 2:
                togo.from_polar((1.5, self.rand.triangular(-180, 180) + lp[1]))
                n = last + togo
                self.ionised.append(n)
            else:
                self.flashing = False
                return


class Bird(Sprite):
    def __init__(self, rect):
        # Call the parent class (Sprite) constructor        if self.flashing or self.pulse < self.pulse_duration:

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

    def set_action(self, start, end, action):
        self.next_action = action
        self.start = pygame.math.Vector2(start)
        self.end = pygame.math.Vector2(end)
        self.ionised = [self.start]
        self.speed = 3
        super().__init__()

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
        if self.ticks % 5 == 0:
            self.active_frame += 1
            self.active_frame = self.active_frame % len(self.actions[self.action])
            if self.active_frame == 0:
                self.action = self.next_action

        self.image.fill((255, 255, 255, 0,))
        self.image.blit(self.frames[self.actions[self.action][self.active_frame]], (0, 0))



        if self.action == 'takeoff':
            self.set_action('flap')

        if self.action == 'rotate_camera':
            self.set_action('soar')

        self.ticks += 1

    def end(self):
        raise StopIteration



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
        self.pole = Vector2(16, 16)
        self.patterns = {'ursamajor': (
                                      Vector2(8, 5),
                                      Vector2(10, 6),
                                      Vector2(8, 10),
                                      Vector2(10, 10),
                                      Vector2(6, 12),
                                      Vector2(5, 14),
                                      Vector2(5, 17)
                                      )
        }
        self.rect = pygame.Rect(x, y, 31, 31)
        # Call the parent class (Sprite) constructor
        Sprite.__init__(self, 32, 32)

        self.angle = 180
        self.dangle = 2

    def update(self):
        self.image.fill(white)

        self.image.set_at((int(self.pole.x), int(self.pole.y)), (255,229,0) )
        for star in self.patterns['ursamajor']:


            star = star.rotate(self.angle) + self.pole
            self.image.set_at((int(star.x), int(star.y)), (255,229,0) )

        self.angle = (self.angle + self.dangle) % 360

    def end(self):
        raise StopIteration

class HSMoon(MoveableThing):
    def __init__(self, pos, size, fade_duration = None):
        super().__init__(pos, size, fade_duration)
        self.raw_base = pygame.image.load(os.path.join('Resources', 'moon_base.png'))
        self.raw_base = self.raw_base.convert()
        self.raw_overlay = pygame.image.load(os.path.join('Resources', 'moon_overlay.png'))
        self.raw_overlay = self.raw_overlay.convert()
        self.scaled_base = None
        self.scaled_overlay = None

        self.overlay_pos = 0.0
        self.overlay_rate = 0.0
        self.overlay_enabled = False

    def overlay(self, fade_duration = None):
        if fade_duration is None:
            self.overlay_enabled = False
        else:
            self.overlay_enabled = True
            self.overlay_rate = math.pi * 2 / (get_fps() * fade_duration)

    def update(self):
        super().update()
        size = int(round(self.size * 2))
        image_size = (size, size)
        if self.overlay_rate != 0.0:
            self.overlay_pos += self.overlay_rate
            if self.overlay_pos > math.pi * 2.0:
                self.overlay_pos -= math.pi * 2.0
                if not self.overlay_enabled:
                    self.overlay_rate = 0.0
                    self.overlay_pos = 0.0
        if self.scaled_base is None or self.scaled_base.get_size() != image_size:
            self.scaled_base = pygame.transform.scale(self.raw_base, image_size)
            self.scaled_base.set_colorkey(black)
            self.scaled_overlay = pygame.transform.scale(self.raw_overlay, image_size)
            self.scaled_overlay.set_colorkey(black)

    def draw(self, surface):
        pos = (int(self.x - self.size), int(self.y - self.size))
        alpha = int(255 * self.fade)
        self.scaled_base.set_alpha(alpha)
        surface.blit(self.scaled_base, pos)
        alpha = int(255 * (1.0 - math.cos(self.overlay_pos)) / 2)
        if alpha > 0:
            self.scaled_overlay.set_alpha(alpha)
            surface.blit(self.scaled_overlay, pos)

def pythagoras(vector):
    return math.sqrt(vector[0] * vector[0] + vector[1] * vector[1])


class Wave(Sprite):
    def __init__(self, direction, width):
        super().__init__()
        self.width = width
        self.direction = direction
        speed = pythagoras(direction)
        self.norm = (direction[1] / speed, -direction[0] / speed)
        self.max_x = MADRIX_X
        self.max_y = MADRIX_Y
        if direction[0] > 0.0:
            start_x = 0.0
        else:
            start_x = self.max_x
        if direction[1] > 0.0:
            start_y = 0.0
        else:
            start_y = self.max_y
        self.pos = (start_x, start_y)

    def update(self):
        x = self.pos[0] + self.direction[0]
        y = self.pos[1] + self.direction[1]
        self.pos = (x, y)
        d = self.distance((0, 0))
        d = min(d, self.distance((0, self.max_y)))
        d = min(d, self.distance((self.max_x, self.max_y)))
        d = min(d, self.distance((self.max_x, 0)))
        if d > self.width * 2.0 + 1.0:
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

def colormixer(color):
    def do_mix(orig, value):
        (r, g, b) = orig
        if color & 1:
            r = max(r, value)
        if color & 2:
            g = max(g, value)
        if color & 4:
            b = max(b, value)
        return (r, g, b)
    return do_mix

class Beacon(Sprite):
    red = 1
    green = 2
    blue = 4
    purple = red + blue
    yellow = red + green
    cyan = green + blue
    colors = [
        red,
        green,
        purple,
        cyan,
    ]

    def __init__(self, pos, color, max_r, speed):
        super().__init__()
        self.pos = pos
        self.radius = 0.5
        self.triggered = False
        self.max_r = max_r
        self.speed = speed
        self.color = color

    def update(self):
        self.radius += self.speed
        if self.radius > self.max_r:
            self.kill()

    def distance(self, point):
        x = point[0] - self.pos[0]
        y = point[1] - self.pos[1]
        return pythagoras((x, y))

    def mix(self, color, value):
        (r, g, b) = color
        if self.color & 1:
            r = max(r, value)
        if self.color & 2:
            g = max(g, value)
        if self.color & 4:
            b = max(b, value)
        return (r, g, b)

class ProtoWave(object):
    def __init__(self, delay, width, angle):
        self.delay = int(delay)
        self.width = width
        self.angle = angle * math.pi * 2 / 360
    def update(self):
        self.delay -= 1
        return self.delay < 0

class Sea(Group):
    def __init__(self, wave_speed, beacon_speed, beacon_size):
        super().__init__()
        size = (MADRIX_X, MADRIX_Y)
        self.s = pygame.Surface(size, flags = pygame.SRCALPHA)
        self.time = 0
        self.beacons = Group()
        self.num_beacons = 0
        self.future = []
        self.wave_speed = wave_speed
        self.beacon_speed = beacon_speed
        self.beacon_size = beacon_size

    def spawn(self, width, angle, num_waves, interval):
        """Trigger a set of waves"""
        dt = interval * get_fps()
        for i in range(num_waves):
            pw = ProtoWave(dt * i, width, angle)
            self.future.append(pw)

    def add_wave(self, pw):
        direction = (math.cos(pw.angle) * self.wave_speed, math.sin(pw.angle) * self.wave_speed)
        self.add(Wave(direction, pw.width))

    def beacon(self, n):
        self.num_beacons = n

    def wave_collision(self, pos):
        for wave in self:
            dist = wave.distance(pos)
            if dist >= 0 and dist < self.wave_speed * 2.0:
                return True
        return False

    def add_beacon(self):
        while True:
            lamp = self.rand.choice(ceiling.bubbleroof_lamps)
            pos = (lamp.x, lamp.y)
            if not self.wave_collision(pos):
                break;
        color = self.rand.choice(Beacon.colors)
        b = Beacon(pos, color, self.beacon_size, self.beacon_speed)
        self.beacons.add(b)

    def end(self):
        self.num_waves = 0

    def update(self):
        if len(self.beacons) < self.num_beacons:
            self.add_beacon()

        if len(self.future) == 0 and len(self) == 0:
            raise StopIteration

        tomorrow = []
        for pw in self.future:
            if pw.update():
                self.add_wave(pw)
            else:
                tomorrow.append(pw)
        self.future = tomorrow

        for wave in self:
            wave.update()

        for b in self.beacons:
            if b.triggered:
                b.update()
            elif self.wave_collision(b.pos):
                b.triggered = True

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
                close = None
                for wave in self:
                    dist = wave.distance((x, y))
                    if dist > 0.0:
                        if dist < 1.0:
                            dist -= 1.0
                        else:
                            dist = (dist - 1.0) / wave.width
                        if close is None or dist < close:
                            close = dist
                color = (0, 0, 0)
                if close is not None:
                    if close <= 0.0:
                        p = int(255 * (close + 1.0))
                        color = (p, p, p)
                    elif close < 1.0:
                        p = int(255 * (1.0 - close))
                        color = (p, p, 255)
                    elif close < 2.0:
                        p = int(255 * (2.0 - close))
                        color = (0, 0, p)
                height = 0.0
                mix = None
                for b in self.beacons:
                    dist = b.distance((x, y))
                    if dist < b.radius:
                        if dist > b.radius - 1.0:
                            new_height = 1.0
                        else:
                            new_height = dist / b.radius
                    elif dist < b.radius + 1.0:
                        dr = dist - b.radius
                        new_height = math.cos(dr * math.pi / 2.0)
                    else:
                        new_height = 0.0
                    new_height *= min(2.0*math.cos((b.radius / b.max_r) * math.pi / 2.0), 1.0)
                    if new_height > height:
                        height = new_height
                        mix = b.mix
                if mix is not None:
                    intens = int(255 * height)
                    color = mix(color, intens)
                r = color[0]
                g = color[1]
                b = color[2]
                alpha = max(r, g, b)
                if alpha < 255:
                    r = min(r * 255, 255)
                    g = min(g * 255, 255)
                    b = min(b * 255, 255)
                color = (r, g, b, alpha)
                a[x, y] = color
        del a
        surface.blit(self.s, (0, 0))



class Ripples(Sprite):
    def __init__(self, size):
        super().__init__( size[0], size[1], pygame.SRCALPHA)
        self.rect = pygame.Rect((0,0), size)
        self.ticks = 0
        self.alpha = 0

    def takeoff(self):
        self.dspeed = 1
        self.speed = 0




    def update(self):
        water_blue = hlsa_to_rgba(210, 60, 70, 0)

        if self.ticks < 180:
            self.alpha += 128/180
            self.image.fill(hlsa_to_rgba(210, 60, 70, self.alpha))

        else:

            px = pygame.PixelArray(self.image)
            for lamp in ceiling.lamps:
                i = lamp.x
                j = lamp.y
            #for j in range(self.rect.height):
            #    for i in range(self.rect.width):
                water_blue[3] = int(128 + ((math.sin(i + self.ticks/50) - math.sin(j))) * ((0.5 * math.sin(self.ticks/15)))  * min(self.ticks*0.1, 64))
                px[i, j] = tuple(water_blue)
            del(px)
        self.ticks += 1


class PlasmaBlob(Sprite):
    def __init__(self, pos, size, duration, angle, color):
        super().__init__()
        self.x = pos[0]
        self.y = pos[1]
        self.width = size[0]
        self.height = size[1]
        rad = angle * math.pi * 2.0 / 360
        self.cos = math.cos(rad)
        self.sin = math.sin(rad)
        if self.width < self.height:
            Exception("Wibble")
        self.ell = self.width + self.height
        self.speed = 1.0 / (get_fps() * duration)
        self.time = 0.0
        self.color = color

    def update(self):
        self.time += self.speed
        if self.time > 2.0:
            self.kill()

    def draw(self, pixels):
        for lamp in ceiling.lamps:
            x = lamp.x
            y = lamp.y
            dx = x - self.x
            dy = y - self.y
            du = (dx * self.cos + dy * self.sin) / self.width
            dv = (dy * self.cos - dx * self.sin) / self.height
            dist = pythagoras((du, dv))
            if dist > 1.0:
                continue
            dist = dist * dist
            height = (1.0 - math.cos(dist * math.pi * 2.0)) / 2.0
            sd = self.time - dist
            if sd < 0 or sd > 1.0:
                continue
            shade = height * (1.0 - math.cos(sd * math.pi * 2)) / 2.0
            r = int(self.color[0] * shade)
            g = int(self.color[1] * shade)
            b = int(self.color[2] * shade)
            prev = pixels[x, y]
            if prev != 0:
                r = max(r, (prev >> 16) & 0xff)
                g = max(g, (prev >> 8) & 0xff)
                b = max(b, prev & 0xff)
            pixels[x, y] = (r, g, b)

class Aurora(Group):
    blob_colors = [
        (128, 0, 0),
        (255, 0, 255),
        (0, 0, 128),
        (0, 255, 0),
    ]
    def __init__(self, pos, blob_duration, num_blobs):
        super().__init__()
        self.x = pos[0]
        self.y = pos[1]
        self.time = 0.0
        self.speed = 0.0
        self.blob_duration = blob_duration
        self.num_blobs = 0
        self.rate = 0.0
        self.s = pygame.Surface(MADRIX_SIZE)
        self.s.set_colorkey(black)
        self.spawn(num_blobs)

    def spawn(self, n):
        self.num_blobs = n
        self.rate = n / (get_fps() * self.blob_duration)

    def add_blob(self):
        width = 20
        height = 3
        x = self.x + self.rand.randrange(-width, width)
        y = self.y + self.rand.randrange(-height, height)
        angle = self.rand.randrange(360)
        color = self.rand.choice(self.blob_colors)
        self.add(PlasmaBlob((x, y), (width, height), self.blob_duration, angle, color))

    def update(self):
        super().update()
        self.time -= self.rate * self.rand.random()
        if self.time < 0.0 and len(self) < self.num_blobs:
            self.add_blob()
            self.time += 1.0
        if self.num_blobs == 0 and len(self) == 0:
            raise StopIteration

    def draw(self, surface):
        self.s.fill(0)
        pixels = pygame.PixelArray(self.s)
        for blob in self:
            blob.draw(pixels)
        del pixels
        surface.blit(self.s, (0,0))

    def end(self):
        self.num_blobs = 0
