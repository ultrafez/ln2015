#! /usr/bin/env python3
import logging

logging.basicConfig()

from ln_objects import *
import pygame
from pygame.event import Event

import subprocess as sp
import platform
import glob
import sys

__author__ = 'ajtag'

black = 0, 0, 0
red = 255, 0, 0
white = 255, 255, 255

FPS = 24
MADRIX_X = 132
MADRIX_Y = 70
SCALE = 8

class Trigger(object):
    """Create a new Group, or run a method on an existing group"""
    def __init__(self, scene, method=None, args=()):
        self.scene = scene
        self.method = method
        self.args = args
    def __repr__(self):
        return "Trigger(%s,%s,%s)" % (self.scene, self.method, self.args)

key_triggers = {
    pygame.K_q: Trigger("STARS"),
    pygame.K_a: Trigger("SUNRISE"),
    pygame.K_w: Trigger("STARS", "fade"),
    pygame.K_e: Trigger("STARS", "end"),
    pygame.K_z: Trigger("CLOUDS"),
    pygame.K_d: Trigger("LIGHTNING"),
    pygame.K_c: Trigger("RAIN"),
    pygame.K_f: Trigger("LIGHTNING", "end"),
    pygame.K_g: Trigger("WAVES"),
    pygame.K_x: Trigger("CLOUDS", "end"),
    pygame.K_v: Trigger("RAIN", "end"),
    pygame.K_r: Trigger("BOUYS"),
    pygame.K_y: Trigger("BIRDS"),
    pygame.K_t: Trigger("BOUYS", "end"),
    pygame.K_h: Trigger("WAVES", "end"),
    pygame.K_b: Trigger("FOREST"),
    pygame.K_u: Trigger("BIRDS", "end"),
    pygame.K_n: Trigger("FOREST", "end"),
    pygame.K_j: Trigger("SUNSET"),
    pygame.K_i: Trigger("CONSTALATION"),
    pygame.K_k: Trigger("SUNSET", "end"),
    pygame.K_p: Trigger("NORTHERNLIGHTS"),
    pygame.K_LEFTBRACKET: Trigger("NORTHERNLIGHTS", "end"),
    pygame.K_m: Trigger("MOONRISE"),
    pygame.K_COMMA: Trigger("MOONRISE", "end"),
    pygame.K_o: Trigger("CONSTALATION", "end")
}

EVENT_TIMING = {
    0 * FPS: [Trigger("STARS"), Trigger("HS_SPIN")],  # Star Sounds and CricketsStart
    30 * FPS: [Trigger("SUNRISE"), Trigger("STARS", "fade")],  # Bird Song Dawn ChorusStart Stars and Crickets FadeEnd
    40 * FPS: [Trigger("STARS", "end")],  # Star Sounds and CricketsEnd
    60 * FPS: [Trigger("CLOUDS")],  # Clouds and Wind SoundsStart
    100 * FPS: [Trigger("LIGHTNING"), # Fork and Sheet Lightning SoundsStart
        Trigger("LIGHTNING", "add_sheet", (pygame.Rect(33, 44, 30, 30),)),  
        Trigger("LIGHTNING", "add_sheet", (pygame.Rect(77, 38, 50, 15),))],

    110 * FPS: [Trigger("RAIN")],  # Rain SoundsStart
    140 * FPS: [Trigger("LIGHTNING", "end")],  # Lightning SoundsEnd
    150 * FPS: [Trigger("WAVES")],  # Wave and Ambient SoundsStart
    180 * FPS: [Trigger("CLOUDS", "end"), Trigger("RAIN", "end")],  # Clouds FadeEnd #Rain SoundsEnd
    200 * FPS: [Trigger("BOUYS")],  # Waves Ring Bouys to MakeSounds
    220 * FPS: [Trigger("BIRDS")],  # Sea Birds SoundsStart
    240 * FPS: [Trigger("BOUYS", "end")],  # Buoys SoundsStop
    250 * FPS: [Trigger("FOREST")],  # Forest SoundsStarts
    260 * FPS: [Trigger("WAVES", "end"), Trigger("SUNSET"), Trigger("BIRDS", "end")],  # Sea Birds SoundsEnd #Waves SoundsEnd
    270 * FPS: [Trigger("CONSTALATION"), Trigger("FOREST", "end")],  # Night Crickets and Star SoundsStart #Forest SoundsEnd
    280 * FPS: [Trigger("SUNSET", "end")],  #
    290 * FPS: [Trigger("NORTHERNLIGHTS")],  # Northern Lights Sounds Start (Ambient Sine Bass Notes?)
    310 * FPS: [Trigger("NORTHERNLIGHTS", "end")],  # Northern Lights SoundsEnd
    300 * FPS: [Trigger("MOONRISE")],  #
    320 * FPS: [Trigger("MOONRISE", "end"), Trigger("CONSTALATION", "end")],  #
}

location_rect ={
    'bubbleroof': pygame.Rect((50, 34), (28, 33)),

    'island': pygame.Rect((0, 41), (12, 7)),
    'left outer arm': pygame.Rect((16, 42), (18, 8)),
    'left inner arm': pygame.Rect((33, 37), (16, 13)),

    'top outer arm': pygame.Rect((61, 1), (0, 18)),
    'top inner arm': pygame.Rect((60, 18), (9, 18)),

    'right inner arm': pygame.Rect((77, 40), (21, 12)),
    'right outer arm': pygame.Rect((97, 40), (28, 12)),
}


scene_data = {
    "STARS":(StarrySky, ((MADRIX_X, MADRIX_Y),)),
    "HS_SPIN":(HSMoon,(1, 38, 4,-45, 0)),
    "SUNRISE":(RisingSun, ((66, 70), (66, 35), 10, FPS * 2, FPS)),
    "CLOUDS":(Clouds, ((MADRIX_X, MADRIX_Y),)),
    "LIGHTNING":(Thunderstorm, ()),
    "RAIN":(Raindrops, ((MADRIX_X, MADRIX_Y),)),
    "MOONRISE":(HSMoon, ()),
}

class LN2015:
    log = logging.getLogger('LN2015')

    def __init__(self, title, width, height, fps, maskonoff=True, save=False):
        self.title = title
        self.width = width
        self.height = height
        self.size = (width, height)
        self.lightmask = maskonoff
        self.mask = pygame.Surface(self.size)
        self.mask.fill((0x30, 0x30, 0x30, 0xff))
        for x, y in ceiling.lamps:
            self.mask.set_at((x, y), (255, 255, 255, 0))
        self.mask.set_colorkey((255, 255, 255))
        self.screen = pygame.Surface(self.size)
        self.display = pygame.display.set_mode((SCALE * MADRIX_X, SCALE * MADRIX_Y))
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.objects = {}
        self.ticks = 0
        self.background = black
        self.log.info('done init')
        self.save_images = True
        self.save_video = save
        self.cursor_loc_start = None
        self.cursor_loc_end = None

    def save(self, x, y, ffmpeg_exe=None):
        if not self.save_video:
            return

        if ffmpeg_exe is None:
            if 'windows' in platform.platform().lower():
                ffmpeg_exe = 'C:\\Users\\admin\\Desktop\\ffmpeg-20150921-git-74e4948-win64-static\\bin\\ffmpeg.exe'
            else:
                ffmpeg_exe = 'ffmpeg'

        command = [ffmpeg_exe,
                   '-y',  # (optional) overwrite output file if it exists
                   '-r', '{}'.format(self.fps),  # frames per second
                   '-i', os.path.join('images', '{}_%d.png'.format(self.title)),
                   '-an',  # Tells FFMPEG not to expect any audio
                   '-c:v', 'libx264',
                   '-s', '{}x{}'.format(x, y),  # size of one frame
                   '{}.mp4'.format(self.title)
                   ]
        sp.call(command)

    def run_trigger(self, trigger):
        if trigger.method is None:
            try:
                d = scene_data[trigger.scene]
            except:
                self.log.error("No such scene '%s'" % trigger.scene)
                return
            try:
                self.objects[trigger.scene] = d[0](*d[1])
            except:
                self.log.error("Failed to create '%s' %s" % (trigger.scene, d))
                raise
        else:
            try:
                try:
                    o = self.objects[trigger.scene]
                except KeyError:
                    self.log.error("Scene '%s' not running")
                    return
                getattr(o, trigger.method)(*trigger.args)
            except StopIteration:
                del self.objects[trigger.scene]
            except:
                self.log.error("%s" % (trigger))
                raise

    def run(self):
        for event in pygame.event.get():

            # Check for quit
            if event.type == pygame.QUIT:
                return False
            # Mouse events
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # left start click
                self.cursor_loc_start = event.pos
                self.cursor_loc_end = None

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # left finish click
                self.cursor_loc_end = event.pos
                print(
                    math.floor(self.cursor_loc_start[0]/SCALE),
                    math.floor(self.cursor_loc_start[1]/SCALE),
                    math.floor((event.pos[0] - self.cursor_loc_start[0])/SCALE),
                    math.floor((event.pos[1] - self.cursor_loc_start[1])/SCALE)
                )

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:  # right click
                self.cursor_loc_start = None
                self.cursor_loc_end = None

            # Check Keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                elif event.key == pygame.K_QUESTION:
                    self.log.info('''
F1 - save video on exit
F2 - view mask
esc - quit
''')

                elif event.key == pygame.K_F1:
                    self.save_video = not self.save_video
                    self.log.warning('save video: {}'.format(self.save_video))

                elif event.key == pygame.K_F2:
                    self.lightmask = not self.lightmask
                    self.log.info('Mask: {}'.format(self.lightmask))

                if event.key in key_triggers:
                    self.log.debug('pressed {}'.format(event.key))
                    self.run_trigger(key_triggers[event.key])


        self.background = black
        self.screen.fill(self.background)

        for e in EVENT_TIMING.get(self.ticks, []):
            self.run_trigger(e)

        remove = []
        for name, element in self.objects.items():
            try:
                element.update()
                element.draw(self.screen)
            except StopIteration:
                remove.append(name)
        for name in remove:
            del self.objects[name]

        self.ticks += 1
        if self.lightmask:
            pygame.Surface.blit(self.screen, self.mask, (0, 0))
        pygame.transform.scale(self.screen, self.display.get_size(), self.display)

        #  draw a red rect overlay to the display surface by dragging the mouse
        if self.cursor_loc_start is not None:
            i, j = self.cursor_loc_start
            if self.cursor_loc_end is None:
                x, y = pygame.mouse.get_pos()
            else:
                x, y = self.cursor_loc_end
            r = pygame.Rect((min(i, x), min(j, y)), (max(i, x) - min(i, x), max(j, y) - min(j, y)))
            pygame.draw.rect(self.display, (255, 0, 0), r, 2)

        pygame.display.flip()

        if self.save_images:
            savepath = os.path.join('images')

            if not (os.path.isdir(savepath)):
                os.mkdir(savepath)

            savefile = os.path.join('images', '{}_{}.png'.format(self.title, self.ticks))
            pygame.image.save(self.screen, savefile)

        self.clock.tick(self.fps)
        return True


if __name__ == "__main__":

    logging.getLogger().setLevel(logging.INFO)
    pygame.init()

    # delete any files saved from previous runs
    [os.unlink(i) for i in glob.glob(os.path.join('images', '*.png'))]

    scene = LN2015('objects', MADRIX_X, MADRIX_Y, FPS, maskonoff=True)

    alive = True
    while alive:
        alive = scene.run()
    scene.save(MADRIX_X, MADRIX_Y)
    pygame.quit()

sys.exit()
