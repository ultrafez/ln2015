import logging
logging.basicConfig()

from ln_objects import *

import subprocess as sp

import platform
import glob
import sys


__author__ = 'ajtag'

black = 0, 0, 0
white = 255, 255, 255

FPS = 24
MADRIX_X = 132
MADRIX_Y = 70
SCALE = 8

STARS_START = 0
SUNRISE_START = FPS * 0
STARS_FADE = FPS * 30
STARS_END = FPS * 40
CLOUDS_START = FPS * 999 #
SUNRISE_END = FPS * 30
LIGHTNING_START = FPS * 100
RAIN_START = FPS * 20 # 110
LIGHTNING_END = FPS * 120
WAVES_START = FPS * 125
CLOUDS_END = FPS * 130
RAIN_END = FPS * 40

BOUYS_START = FPS * 180
BIRDS_START = FPS * 220
BOUYS_END = FPS * 260

WAVES_END = FPS * 370
FOREST_START = FPS * 380
BIRDS_END = FPS * 410

FOREST_END = FPS * 440
SUNSET_START = FPS * 440

CONSTALATION_START = FPS * 490
SUNSET_END = FPS * 510

NORTHERNLIGHTS_START = FPS * 520
NORTHERNLIGHTS_END = FPS * 570

MOONRISE_START = FPS * 30#550
MOONRISE_END = FPS * 60
CONSTALATION_END = FPS * 600


class LN2015:
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    def __init__(self, title, width, height, fps, mask=True, save=False):
        self.title = title
        self.width = width
        self.height = height
        self.size = width, height
        self.lightmask = mask
        self.ceiling = Ceiling(self.width, self.height)
        self.screen = pygame.Surface(self.size)
        self.display = pygame.display.set_mode((SCALE*MADRIX_X, SCALE*MADRIX_Y))
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.objects = {}
        self.ticks = 0
        self.background = black
        self.log.info('done init')
        self.save_images = True
        self.save_video = save

    def save(self, x, y, ffmpegexe = None):
        if not self.save_video:
            return

        if ffmpegexe is None:
            if 'windows' in platform.platform().lower():
                ffmpegexe = 'C:\\Users\\admin\\Desktop\\ffmpeg-20150921-git-74e4948-win64-static\\bin\\ffmpeg.exe'
            else:
                ffmpegexe = 'ffmpeg'

        command = [ ffmpegexe,
        '-y', # (optional) overwrite output file if it exists
        '-r', '{}'.format(self.fps), # frames per second
        '-i', os.path.join('images','{}_%d.png'.format(self.title)),
        '-an', # Tells FFMPEG not to expect any audio
        '-c:v', 'libx264',
        '-s',  '{}x{}'.format(x, y), # size of one frame

        '{}.mp4'.format(self.title) ]

        pipe = sp.call(command)



    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_m:
                    self.lightmask = not self.lightmask

                elif event.key == pygame.K_s:
                    self.save_video = not(self.save_video)
                    self.log.warning('save video: {}'.format(self.save_video))

            if event.type == pygame.QUIT:
                return False


        #background
        #if self.ticks < self.fps * 100:
            #self.background = hls_to_rgb(221, 77, min(self.ticks / 500 * 60, 60))
        #self.background = black
        self.screen.fill( self.background )

        #Scene 1  millis: 0 -> 40000  stars fading in and out, shooting stars in whites and yellows
        if self.ticks < STARS_END:
            if self.ticks == STARS_START:
                self.log.info('======= STARS START =======')
                self.objects['starrynight'] = StarrySky((self.width, self.height), self.ceiling)


            self.objects['starrynight'].update()
            self.objects['starrynight'].draw(self.screen)
            if self.ticks == STARS_FADE:
                self.objects['starrynight'].end()
        elif self.ticks == STARS_END:
            del(self.objects['starrynight'])

        #Scene 2  sunrise millis: 20000 -> 70000  Sunrise from south to full basking sun from in the center
        if (SUNRISE_START) <= self.ticks < (SUNRISE_END):
            if self.ticks == SUNRISE_START:
                self.log.info('======= SUNRISE START =======')
                radius = 80

                south = self.ceiling.get_named_position('SOUTH')
                east = self.ceiling.get_named_position('EAST')
                self.objects['sun'] = RisingSun(400, 100, pygame.Rect(400, 330, 20, 150), radius, 40)

            # sunrise from 6AM to 12noon -> 0 to pi/2

            self.objects['sun'].set_height(((self.ticks - SUNRISE_START)/(SUNRISE_END - SUNRISE_START)))
            self.objects['sun'].draw(self.screen)

        elif self.ticks == SUNRISE_END:
            del(self.objects['sun'])

        # Scene 3: clouds  millis: 55 -> 100 white clouds come in from arms and pass, then getting denser, finally covering the sun and going grey.
        if (CLOUDS_START) <= self.ticks < (CLOUDS_END):
            if (self.ticks == CLOUDS_START):
                self.objects['clouds'] = Clouds(self.size)
                self.log.info('======= CLOUDS START =======')

            self.objects['clouds'].update()
            self.objects['clouds'].draw(self.screen)

        # Scene 4: lightning sheet and fork lightning happen
        if (LIGHTNING_START) < self.ticks < (LIGHTNING_END):
            if (self.ticks == LIGHTNING_START):
                self.objects['ligtning'] = Lightning()
                self.log.info('======= LIGHTNING START =======')

        # # Scene 5: rain  rain starts falling with blue splashes, to a torrent, flooding the ceiling
        if (RAIN_START) <= self.ticks < (RAIN_END):
            if RAIN_START == self.ticks:
                self.objects['raindrops'] = Raindrops(self.size)
            self.objects['raindrops'].update()
            self.objects['raindrops'].draw(self.screen)

        # Scene 6: wash     cresting waves crash over the ceiling
        # if (CLOUDS_START) < self.ticks < (CLOUDS_END):
        #     pass
        # # Scene 7: waves calm to a steady roll
        # if (CLOUDS_START) < self.ticks < (CLOUDS_END):
        #     pass
        # # Scene 8:   bouys clank, flashing green and red, as they rock.
        # if (CLOUDS_START) < self.ticks < (CLOUDS_END):
        #     pass
        # # Scene 9  birds come into shot, and takes off, flying inland to the forest,
        # if (CLOUDS_START) < self.ticks < (CLOUDS_END):
        #     pass
        # # Scene 10  forest fades into evening sunlight
        # if (CLOUDS_START) < self.ticks < (CLOUDS_END):
        #     pass
        # # Scene 11  sunset
        # if (CLOUDS_START) < self.ticks < (CLOUDS_END):
        #     pass
        # # Scene 12  northern lights
        # if (CLOUDS_START) < self.ticks < (CLOUDS_END):
        #     pass
        # # Scene 13  north star + night sky
        # if (CLOUDS_START) < self.ticks < (CLOUDS_END):
        #     pass
        # # Scene 14 moon rise with hackspace logo.
        if (MOONRISE_START) <= self.ticks < (MOONRISE_END):
            if self.ticks == MOONRISE_START:
                self.objects['moon'] = HSMoon()

            self.objects['moon'].update()
            self.objects['moon'].draw(self.screen)
            pass


        self.ticks += 1

        if not self.lightmask:
            self.screen.blit(source=self.ceiling.mask, dest=(0, 0))
        pygame.transform.scale(self.screen, self.display.get_size(), self.display)
        pygame.display.flip()

        if self.save_images:
            savepath = os.path.join('images')

            if not(os.path.isdir(savepath)):
                os.mkdir(savepath)


            savefile =   os.path.join('images', '{}_{}.png'.format(self.title, self.ticks))
            pygame.image.save(self.screen, savefile)

        self.clock.tick(self.fps)
        return True


if __name__ == "__main__":
    pygame.init()

    ## delete any files saved from previous runs
    [os.unlink(i) for i in glob.glob(os.path.join('images', '*.png'))]

    scene = LN2015('objects', MADRIX_X, MADRIX_Y, FPS, mask=True)

    alive = True
    while alive:
        alive = scene.run()
    scene.save(MADRIX_X, MADRIX_Y)
    pygame.quit()



sys.exit()

