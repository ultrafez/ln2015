#! /usr/bin/env python3
import sys
sys.path.append('TrinRoofPlayer')

# import pygame
# from TrinRoofPlayer.Renderer import Player, clean_images, Trigger, cmd_line_args
# from TrinRoofPlayer.Objects import *
# from TrinRoofPlayer.Constants import *
# import argparse
from alex_objects import *
import logging
import platform
import random


__author__ = 'ajtag'


logging.basicConfig()

FPS = 24
TOTAL_TIME = 360

key_triggers = {
    # pygame.K_MINUS:Trigger("LIGHTNING_high", "add_sheet", left_outer_arm),
    # pygame.K_EQUALS: Trigger("LIGHTNING_low", "add_fork", MADRIX_SIZE, (130, 55), (0, 55)),
    # pygame.K_q: Trigger("STARS"),
    # pygame.K_a: Trigger("SUNRISE"),
    # pygame.K_z: Trigger("CLOUDS"),
    # pygame.K_d: Trigger("LIGHTNING_high"),
    # pygame.K_f: Trigger("LIGHTNING_low"),
    # pygame.K_c: Trigger("RAIN"),
    # pygame.K_0: Trigger("LIGHTNING", "end"),
    # pygame.K_g: Trigger("WAVES"),
    # pygame.K_v: Trigger("RAIN", "end"),

    # pygame.K_y: Trigger("BIRDS"),
    # pygame.K_1: Trigger("BIRDS", "set_action", 'bob'),
    # pygame.K_2: Trigger("BIRDS", "set_action", 'takeoff'),
    # pygame.K_3: Trigger("BIRDS", "set_action", 'rotate_camera'),

    # pygame.K_h: Trigger("WAVES", "end"),
    # pygame.K_b: Trigger("FOREST"),
    # pygame.K_u: Trigger("BIRDS", "end"),
    # pygame.K_n: Trigger("FOREST", "end"),
    # pygame.K_j: Trigger("SUNSET"),
    # pygame.K_i: Trigger("CONSTELLATION"),
    # pygame.K_k: Trigger("SUNSET", "end"),
    # pygame.K_p: Trigger("AURORA"),
    # pygame.K_LEFTBRACKET: Trigger("AURORA", "end"),
    # pygame.K_m: Trigger("MOONRISE"),
    # pygame.K_COMMA: Trigger("MOONRISE", "move", (66, 53), 12, 10),
    # pygame.K_o: Trigger("CONSTELLATION", "end")
}

WAVE_END_TIME = 215
SUNSET_TIME = 219

EVENT_TIMING = [
    (  0, [Trigger("FATBLOBS")]),
]


scene_data = {
    "FATBLOBS": (0, FatBlobs),
}


if __name__ == "__main__":

    random.seed('taaaash')

    logging.getLogger().setLevel(logging.INFO)
    pygame.init()
    
    args = cmd_line_args()
    print(args)

    clean_images()

    LN2015 = Player('objects', MADRIX_X, MADRIX_Y, fps=FPS, args=args)

    for key, trig in key_triggers.items():
        LN2015.set_key_triggers(key, trig)

    for scene, data in scene_data.items():
        LN2015.load_scene(scene, *data)

    for ticks, events in EVENT_TIMING:
        LN2015.load_timed_event(ticks, events)

    #LN2015.load_sprite('ripples', 100, ripples((MADRIX_X, MADRIX_Y)))

    alive = True
    while alive:
        alive = LN2015.run()

        if 'windows' in platform.platform().lower():
            ffmpeg_exe = 'C:\\Users\\admin\\Desktop\\ffmpeg-20150921-git-74e4948-win64-static\\bin\\ffmpeg.exe'
        elif args.avconv:
            ffmpeg_exe = 'avconv'
        else:
            ffmpeg_exe = 'ffmpeg'          
        if LN2015.ticks > TOTAL_TIME * FPS:
            alive = False
    LN2015.export_video(ffmpeg_exe)
    LN2015.end()

sys.exit()
