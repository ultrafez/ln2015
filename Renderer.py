__author__ = 'ajtag'

import subprocess as sp
import glob
import pygame
import logging
from ln_objects import *
from Constants import *


pygame.font.init()
FONT = pygame.font.Font(None, 24)


class Trigger(object):
    """Create a new Group, or run a method on an existing group"""
    def __init__(self, scene, method=None, args=()):
        self.scene = scene
        self.method = method
        self.args = args

    def __repr__(self):
        return "Trigger(%s,%s,%s)" % (self.scene, self.method, self.args)


def clean_images():
    # delete any files saved from previous runs
    [os.unlink(i) for i in glob.glob(os.path.join('images', '*.png'))]


class Player:
    log = logging.getLogger('Player')

    def __init__(self, title, width, height, display_scale=1.0, fps=24, args=()):
        self.title = title
        self.width = width
        self.height = height
        self.size = (width, height)
        self.display_scale = display_scale
        self.lightmask = args.mask
        self.mask = pygame.Surface(self.size)
        self.mask.fill(dark_grey)
        self.mask.set_colorkey(white)
        for x, y in ceiling.lamps:
            self.mask.set_at((x, y), white)
        self.screen = pygame.Surface(self.size)
        self.display = pygame.display.set_mode((display_scale * width, display_scale * height))
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.objects = {}
        self.ticks = 0
        self.background = black
        self.save_images = args.save_images
        self.save_video = args.save_video
        self.cursor_loc_start = None
        self.cursor_loc_end = None
        self.warp = int(self.fps * args.warp)
        if self.warp != 0 and (self.save_images or self.save_video):
            raise Exception("Can not save when warping")
        self.quick = args.quick

        self.scene_data = {}
        self.key_triggers = {}
        self.timed_events = {}

        self.log.info('done init')

    def set_key_triggers(self, key, trig):
        self.key_triggers[key] = trig

    def load_scene(self, scene_name, scene_data):
        self.scene_data[scene_name] = scene_data

    def load_timed_event(self, ticks, events):
        current_events = self.timed_events.get(ticks, [])
        for e in events:
            current_events.append(e)
        self.timed_events[ticks] = current_events

    def export_video(self, x, y, ffmpeg_exe='ffmpeg'):
        if not self.save_video:
            return

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
                d = self.scene_data[trigger.scene]
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
                    math.floor(self.cursor_loc_start[0]/self.display_scale),
                    math.floor(self.cursor_loc_start[1]/self.display_scale),
                    math.floor((event.pos[0] - self.cursor_loc_start[0])/self.display_scale),
                    math.floor((event.pos[1] - self.cursor_loc_start[1])/self.display_scale)
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
F3 - toggle fps limiter
esc - quit
''')

                elif event.key == pygame.K_F1:
                    self.save_video = not self.save_video
                    self.log.warning('save video: {}'.format(self.save_video))

                elif event.key == pygame.K_F2:
                    self.lightmask = not self.lightmask
                    self.log.info('Mask: {}'.format(self.lightmask))
                elif event.key == pygame.K_F3:
                    self.quick = not self.quick
                    self.log.info('FPS de-limiter: {}'.format(self.quick))

                if event.key in self.key_triggers:
                    self.log.debug('pressed {}'.format(event.key))
                    self.run_trigger(self.key_triggers[event.key])

        self.background = black
        self.screen.fill(self.background)

        for e in self.timed_events.get(self.ticks, []):
            self.run_trigger(e)

        draw = (self.ticks >= self.warp) or (self.ticks % self.fps == 0)
        remove = []
        for name, element in self.objects.items():
            try:
                element.update()
                if draw:
                    element.draw(self.screen)
            except StopIteration:
                remove.append(name)
        for name in remove:
            del self.objects[name]

        self.ticks += 1

        if draw:
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

            self.display.blit(FONT.render('{:.2f}/{:0} fps'.format(self.clock.get_fps(), self.fps), False, (255, 0, 0), ), (10,10))
            self.display.blit(FONT.render('{:02d}:{:02d}.{:02d}'.format(
                    int(1.0*self.ticks/60.0/self.fps),
                    int((self.ticks/self.fps) % 60),
                    self.ticks % self.fps
                ), False, (255, 0, 0),), (10,45))

            pygame.display.flip()

        if self.save_images:
            savepath = os.path.join('images')

            if not (os.path.isdir(savepath)):
                os.mkdir(savepath)

            savefile = os.path.join('images', '{}_{}.png'.format(self.title, self.ticks))
            pygame.image.save(self.screen, savefile)

        if self.ticks == self.warp:
            self.log.info("Warp finished")

        if draw:
            if self.quick:
                self.clock.tick()
            else:
                self.clock.tick(self.fps)

        return True