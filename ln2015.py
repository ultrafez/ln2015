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

HS_SPIN_START_EVENT = Event(pygame.USEREVENT, {'objects': 'HS', 'method': 'START'})  # start HS logo spinning in the egg
STARS_START_EVENT = Event(pygame.USEREVENT, {'objects': 'STARS', 'method': 'START'})  # Star Sounds and Crickets Start
SUNRISE_START_EVENT = Event(pygame.USEREVENT, {'objects': 'SUNRISE', 'method': 'START'})  # Bird Song Dawn Chorus Start
STARS_FADE_EVENT = Event(pygame.USEREVENT, {'objects': 'STARS', 'method': 'FADE'})  # Stars and Crickets Fade End
STARS_END_EVENT = Event(pygame.USEREVENT, {'objects': 'STARS', 'method': 'END'})  # Star Sounds and Crickets End
SUNRISE_END_EVENT = Event(pygame.USEREVENT, {'objects': 'SUNRISE', 'method': 'END'})  # Sun is Risen
CLOUDS_START_EVENT = Event(pygame.USEREVENT, {'objects': 'CLOUDS', 'method': 'START'})  # Clouds and Wind Sounds Start
# Fork and Sheet Lightning Sounds Start
LIGHTNING_START_EVENT = Event(pygame.USEREVENT, {'objects': 'LIGHTNING', 'method': 'START'})
RAIN_START_EVENT = Event(pygame.USEREVENT, {'objects': 'RAIN', 'method': 'START'})  # Rain Sounds Start
LIGHTNING_END_EVENT = Event(pygame.USEREVENT, {'objects': 'LIGHTNING', 'method': 'END'})  # Lightning Sounds End
WAVES_START_EVENT = Event(pygame.USEREVENT, {'objects': 'WAVES', 'method': 'START'})  # Wave and Ambient Sounds Start
CLOUDS_END_EVENT = Event(pygame.USEREVENT, {'objects': 'CLOUDS', 'method': 'END'})  # Clouds Fade End
RAIN_END_EVENT = Event(pygame.USEREVENT, {'objects': 'RAIN', 'method': 'END'})  # Rain Sounds End
BOUYS_START_EVENT = Event(pygame.USEREVENT, {'objects': 'BOUYS', 'method': 'START'})  # Waves Ring Bouys to Make Sounds
BIRDS_START_EVENT = Event(pygame.USEREVENT, {'objects': 'BIRDS', 'method': 'START'})  # Sea Birds Sounds Start
BOUYS_END_EVENT = Event(pygame.USEREVENT, {'objects': 'BOUYS', 'method': 'END'})  # Buoys Sounds Stop
WAVES_END_EVENT = Event(pygame.USEREVENT, {'objects': 'WAVES', 'method': 'END'})  # Waves Sounds End
FOREST_START_EVENT = Event(pygame.USEREVENT, {'objects': 'FOREST', 'method': 'START'})  # Forest Sounds Starts
BIRDS_END_EVENT = Event(pygame.USEREVENT, {'objects': 'BIRDS', 'method': 'END'})  # Sea Birds Sounds End
FOREST_END_EVENT = Event(pygame.USEREVENT, {'objects': 'FOREST', 'method': 'END'})  # Forest Sounds End
SUNSET_START_EVENT = Event(pygame.USEREVENT, {'objects': 'SUNSET', 'method': 'START'})  #
CONSTALATION_START_EVENT = Event(pygame.USEREVENT, {'objects': 'CONSTALATION', 'method': 'START'})
# Night Crickets and Star Sounds Start
SUNSET_END_EVENT = Event(pygame.USEREVENT, {'objects': 'SUNSET', 'method': 'END'})  #
#  Northern Lights Sounds Start (Ambient Sine Bass Notes ?)
NORTHERNLIGHTS_START_EVENT = Event(pygame.USEREVENT, {'objects': 'NORTHERNLIGHTS', 'method': 'START'})
# Northern Lights Sounds End
NORTHERNLIGHTS_END_EVENT = Event(pygame.USEREVENT, {'objects': 'NORTHERNLIGHTS', 'method': 'END'})
MOONRISE_START_EVENT = Event(pygame.USEREVENT, {'objects': 'MOONRISE', 'method': 'START'})  #
MOONRISE_END_EVENT = Event(pygame.USEREVENT, {'objects': 'MOONRISE', 'method': 'END'})  #
CONSTALATION_END_EVENT = Event(pygame.USEREVENT,
                               {'objects': 'CONSTALATION', 'method': 'END'})  # Night Crickets and Star Sounds End

key_triggers = {
    pygame.K_q: STARS_START_EVENT,
    pygame.K_a: SUNRISE_START_EVENT,
    pygame.K_w: STARS_FADE_EVENT,
    pygame.K_e: STARS_END_EVENT,
    pygame.K_s: SUNRISE_END_EVENT,
    pygame.K_z: CLOUDS_START_EVENT,
    pygame.K_d: LIGHTNING_START_EVENT,
    pygame.K_c: RAIN_START_EVENT,
    pygame.K_f: LIGHTNING_END_EVENT,
    pygame.K_g: WAVES_START_EVENT,
    pygame.K_x: CLOUDS_END_EVENT,
    pygame.K_v: RAIN_END_EVENT,
    pygame.K_r: BOUYS_START_EVENT,
    pygame.K_y: BIRDS_START_EVENT,
    pygame.K_t: BOUYS_END_EVENT,
    pygame.K_h: WAVES_END_EVENT,
    pygame.K_b: FOREST_START_EVENT,
    pygame.K_u: BIRDS_END_EVENT,
    pygame.K_n: FOREST_END_EVENT,
    pygame.K_j: SUNSET_START_EVENT,
    pygame.K_i: CONSTALATION_START_EVENT,
    pygame.K_k: SUNSET_END_EVENT,
    pygame.K_p: NORTHERNLIGHTS_START_EVENT,
    pygame.K_LEFTBRACKET: NORTHERNLIGHTS_END_EVENT,
    pygame.K_m: MOONRISE_START_EVENT,
    pygame.K_COMMA: MOONRISE_END_EVENT,
    pygame.K_o: CONSTALATION_END_EVENT
}

EVENT_TIMING = {
    0 * FPS: [STARS_START_EVENT, HS_SPIN_START_EVENT],  # Star Sounds and CricketsStart
    30 * FPS: [SUNRISE_START_EVENT, STARS_FADE_EVENT],  # Bird Song Dawn ChorusStart Stars and Crickets FadeEnd
    40 * FPS: [STARS_END_EVENT],  # Star Sounds and CricketsEnd
    50 * FPS: [SUNRISE_END_EVENT],  # Sun isRisen
    60 * FPS: [CLOUDS_START_EVENT],  # Clouds and Wind SoundsStart
    100 * FPS: [LIGHTNING_START_EVENT],  # Fork and Sheet Lightning SoundsStart
    110 * FPS: [RAIN_START_EVENT],  # Rain SoundsStart
    140 * FPS: [LIGHTNING_END_EVENT],  # Lightning SoundsEnd
    150 * FPS: [WAVES_START_EVENT],  # Wave and Ambient SoundsStart
    180 * FPS: [CLOUDS_END_EVENT, RAIN_END_EVENT],  # Clouds FadeEnd #Rain SoundsEnd
    200 * FPS: [BOUYS_START_EVENT],  # Waves Ring Bouys to MakeSounds
    220 * FPS: [BIRDS_START_EVENT],  # Sea Birds SoundsStart
    240 * FPS: [BOUYS_END_EVENT],  # Buoys SoundsStop
    250 * FPS: [FOREST_START_EVENT],  # Forest SoundsStarts
    260 * FPS: [WAVES_END_EVENT, SUNSET_START_EVENT, BIRDS_END_EVENT],  # Sea Birds SoundsEnd #Waves SoundsEnd
    270 * FPS: [CONSTALATION_START_EVENT, FOREST_END_EVENT],  # Night Crickets and Star SoundsStart #Forest SoundsEnd
    280 * FPS: [SUNSET_END_EVENT],  #
    290 * FPS: [NORTHERNLIGHTS_START_EVENT],  # Northern Lights Sounds Start (Ambient Sine Bass Notes?)
    310 * FPS: [NORTHERNLIGHTS_END_EVENT],  # Northern Lights SoundsEnd
    300 * FPS: [MOONRISE_START_EVENT],  #
    320 * FPS: [MOONRISE_END_EVENT, CONSTALATION_END_EVENT],  #
}

# STARS_START = FPS * 0 #Star Sounds and Crickets Start
# SUNRISE_START = FPS * 30 #Bird Song Dawn Chorus Start
# STARS_FADE = FPS * 30 #Stars and Crickets Fade End
# STARS_END = FPS * 40 #Star Sounds and Crickets End
# SUNRISE_END = FPS * 50 #Sun is Risen
# CLOUDS_START = FPS * 60 #Clouds and Wind Sounds Start
# LIGHTNING_START = FPS * 100 #Fork and Sheet Lightning Sounds Start
# RAIN_START = FPS * 110 #Rain Sounds Start
# LIGHTNING_END = FPS * 140 #Lightning Sounds End
# WAVES_START = FPS * 150 #Wave and Ambient Sounds Start
# CLOUDS_END = FPS * 180 #Clouds Fade End
# RAIN_END = FPS * 180 #Rain Sounds End
# BOUYS_START = FPS * 200 #Waves Ring Bouys to Make Sounds
# BIRDS_START = FPS * 220 #Sea Birds Sounds Start
# BOUYS_END = FPS * 240 #Buoys Sounds Stop
# WAVES_END = FPS * 260 #Waves Sounds End
# FOREST_START = FPS * 250 #Forest Sounds Starts
# BIRDS_END = FPS * 260 #Sea Birds Sounds End
# FOREST_END = FPS * 270 #Forest Sounds End
# SUNSET_START = FPS * 260 #
# CONSTALATION_START = FPS * 270 #Night Crickets and Star Sounds Start
# SUNSET_END = FPS * 280 #
# NORTHERNLIGHTS_START = FPS * 290 #Northern Lights Sounds Start (Ambient Sine Bass Notes ?)
# NORTHERNLIGHTS_END = FPS * 310 #Northern Lights Sounds End
# MOONRISE_START = FPS * 300 #
# MOONRISE_END = FPS * 320 #
# CONSTALATION_END = FPS * 320 #Night Crickets and Star Sounds End

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


class LN2015:
    log = logging.getLogger('LN2015')

    def __init__(self, title, width, height, fps, maskonoff=True, save=False):
        self.title = title
        self.width = width
        self.height = height
        self.size = (width, height)
        self.lightmask = maskonoff
        self.ceiling = Ceiling('Resources/pixels.csv')
        self.mask = pygame.Surface(self.size)
        self.mask.fill((0x30, 0x30, 0x30, 0xff))
        for x, y in self.ceiling.lamps:
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
                    pygame.event.post(key_triggers[event.key])
                    self.log.debug('pressed {}'.format(event.key))

            # Check for animation events
            if event.type == pygame.USEREVENT:
                if event == STARS_START_EVENT:
                    self.objects[event.objects] = StarrySky((self.width, self.height), self.ceiling)
                    self.log.info('======= STARS START =======')

                if event == STARS_FADE_EVENT:
                    try:
                        self.objects[event.objects].end()
                        self.log.info('======= STARS FADE =======')
                    except KeyError:
                        self.log.warning('stars isnt running')

                if event == HS_SPIN_START_EVENT:
                    self.objects[event.objects] = HSMoon(1, 38, 4,-45, 0)

                if event == SUNRISE_START_EVENT:
                    self.objects[event.objects] = RisingSun((66, 70), (66, 35), 10, FPS * 2, FPS)
                    self.log.info('======= SUNRISE START =======')

                if event == CLOUDS_START_EVENT:
                    self.objects[event.objects] = Clouds(self.size)
                    self.log.info('======= CLOUDS START =======')

                if event == LIGHTNING_START_EVENT:

                    storm = Thunderstorm()
                    position = pygame.Rect(0, 0, 30, 30)
                    position.center = (33, 44)
                    storm.add_sheet(position)

                    position = pygame.Rect(77, 38, 50, 15)
                    storm.add_sheet(position)
                    self.objects[event.objects] = storm

                    self.log.info('======= LIGHTNING START =======')

                if event == RAIN_START_EVENT:
                    self.objects[event.objects] = Raindrops(self.size)
                    self.log.info('======= RAIN START =======')

                if event == MOONRISE_START_EVENT:
                    self.objects[event.objects] = HSMoon()

                    self.log.info('======= MOONRISE START =======')

                if event.method == 'END':
                    try:
                        del (self.objects[event.objects])
                        self.log.info('======= {} END ======='.format(event.objects))
                    except KeyError:
                        self.log.warning('{} isnt running'.format(event.objects))

        self.background = black
        self.screen.fill(self.background)

        for e in EVENT_TIMING.get(self.ticks, []):
            pygame.event.post(e)

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
