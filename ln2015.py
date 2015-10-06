#! /usr/bin/env python3
import sys
sys.path.append('TrinRoofPlayer')

from ln_objects import *
import pygame
from TrinRoofPlayer.Renderer import Player, clean_images, Trigger, cmd_line_args
from TrinRoofPlayer.Constants import *
import argparse
import logging
import platform
import random


__author__ = 'ajtag'


logging.basicConfig()

FPS = 24
TOTAL_TIME = 360

key_triggers = {
    pygame.K_MINUS:Trigger("LIGHTNING_high", "add_sheet", left_outer_arm),
    pygame.K_EQUALS: Trigger("LIGHTNING_low", "add_fork", MADRIX_SIZE, (130, 55), (0, 55)),
    pygame.K_q: Trigger("STARS"),
    pygame.K_a: Trigger("SUNRISE"),
    pygame.K_z: Trigger("CLOUDS"),
    pygame.K_d: Trigger("LIGHTNING_high"),
    pygame.K_f: Trigger("LIGHTNING_low"),
    pygame.K_c: Trigger("RAIN"),
    pygame.K_0: Trigger("LIGHTNING", "end"),
    pygame.K_g: Trigger("WAVES"),
    pygame.K_v: Trigger("RAIN", "end"),

    pygame.K_y: Trigger("BIRDS"),
    pygame.K_1: Trigger("BIRDS", "set_action", 'bob'),
    pygame.K_2: Trigger("BIRDS", "set_action", 'takeoff'),
    pygame.K_3: Trigger("BIRDS", "set_action", 'rotate_camera'),

    pygame.K_h: Trigger("WAVES", "end"),
    pygame.K_b: Trigger("FOREST"),
    pygame.K_u: Trigger("BIRDS", "end"),
    pygame.K_n: Trigger("FOREST", "end"),
    pygame.K_j: Trigger("SUNSET"),
    pygame.K_i: Trigger("CONSTELLATION"),
    pygame.K_k: Trigger("SUNSET", "end"),
    pygame.K_p: Trigger("AURORA"),
    pygame.K_LEFTBRACKET: Trigger("AURORA", "end"),
    pygame.K_m: Trigger("MOONRISE"),
    pygame.K_COMMA: Trigger("MOONRISE", "move", (66, 53), 12, 10),
    pygame.K_o: Trigger("CONSTELLATION", "end")
}

WAVE_END_TIME = 215
SUNSET_TIME = 219

EVENT_TIMING = [
    (  0, [Trigger("STARS")]),
    ( 30, Trigger("MORNINGSKY")),
    ( 25, [Trigger("SUNRISE"), Trigger("SUNRISE", "move", (13, 51), 40, 5)]),
    ( 30, [Trigger("SUNRISE", "move", (66, 51), 15, 30)]),
    ( 38, [Trigger("STARS", "end", 5)]),  #fadetime
    ( 53, [Trigger("CLOUDS")]),
    ( 65, Trigger("CLOUDSKY")),
    ( 75, Trigger("MORNINGSKY", "end", 5)),
    ( 75, Trigger("SUNRISE", "move", None, 1, 8)), # newpos, newsize, duration
    ( 75, Trigger("SUNRISE", "end", 10)),  # fadetime
    ( 75, Trigger("CLOUDSKY", "end", 15)),
    ( 85, [Trigger("CLOUDS", "grey", 0.6, 10)]),
    #( 85, Trigger("FOG")),


    #LIGHTNING
    ( 90, [Trigger("LIGHTNING_high"), Trigger("LIGHTNING_high", 'incoming', 10)]),  # start lightning incoming
    (109, [Trigger("LIGHTNING_low"), Trigger("LIGHTNING_low", 'big_hit')]),
    
    #LIGHTNING END RAIN TRANSITION
    (140, [Trigger("LIGHTNING_low", "end")]),  
    (145, [Trigger("RAINSMALL")]),  # start rain and ripples
    (150, [Trigger("LIGHTNING_high", "outgoing", 5)]),  # stop main storm and fade  outer storm
    (151, [Trigger("RAINMID")]),  # start rain and ripples
    (155, [Trigger("LIGHTNING_high", "end")]),  # Lightning End
    (154, [Trigger("RAINBIG")]),  # start rain and ripples
    
    #RIPPLE OCEAN BUILDS (FIX)
    (163, [Trigger("ripples")], ),  # number buoys
    (163, [Trigger("ripples", 'fade_to', 210, 60, 50, 128, 9)]),  # fade brightness up

    #FIRST WAVE
    (173, [Trigger("WAVES"), Trigger("WAVES", "spawn", 20, 180, 1, 3)]),  # width, angle, num_waves, interval

    #END RAIN CLOUDS
    (177.5, [Trigger("RAINSMALL", "end", 0.5)]),
    (177.5, [Trigger("RAINMID", "end", 0.5)]),
    (177.5, [Trigger("RAINBIG", "end", 0.5)]),
    (177.5, [Trigger("ripples", 'fade_to', None, None, None, 0, 0.5)]),
    (177.5, Trigger("CLOUDS", "end", 1.5)), # fadetime
    #(178, Trigger("FOG", "end", 1.5)), # fadetime

    #WAVES AND BEACONS
    (178, [Trigger("WAVES", "spawn", 15, 180, 1, 3)]),
    (183, [Trigger("WAVES", "spawn", 10, 180, 1, 3)]),
    (185, [Trigger("WAVES", "beacon", 1)]),  # number buoys
    (185, [Trigger("WAVES", "spawn", 6, 180, 2, 3)]),
    (192, [Trigger("WAVES", "beacon", 3)]),  # number buoys
    (190, [Trigger("WAVES", "spawn", 4, 180, 10, 2)]),
    (208, [Trigger("WAVES", "spawn", 4, 180, 3, 3)]),
    (208, [Trigger("WAVES", "beacon", 1)]),  # number buoys

    #(214.5, [Trigger("BIRDS"), Trigger("BIRDS", 'set_action', 'bob'), Trigger('ripples', 'fade_to', None, 90, 80, 200, 6)]),  # Sea Birds SoundsStart

    (215, [Trigger("WAVES", "beacon", 0)]),  # number buoys


    #(218, [Trigger("BIRDS", 'set_action', 'takeoff')]),
    #(219.5, [Trigger('ripples', 'takeoff')]),


    #(225, [Trigger("BIRDS", 'set_action', 'rotate_camera')]),
    #(227, [Trigger('ripples', 'rotate')]),
    #(230, [Trigger('ripples', 'fade_out')]),
    #(245, [Trigger("ripples", "end")]),
    #(235, [Trigger("BIRDS", 'exit')]),
    #SUNSET
    (SUNSET_TIME, [Trigger("SUNSET"), Trigger("SUNSET", "move", (None), 15, 5)]),
    (SUNSET_TIME+6, [Trigger("SUNSET", "move", (-40, 51), 50, 30)]), # newpos, newsize, duration
    (SUNSET_TIME+36, [Trigger("SUNSET", "move", None, 0, 10)]), # newpos, newsize, duration
    (SUNSET_TIME+36, [Trigger("SUNSET", "end", 10)]),  # fadetime

    #NIGHTSKY
    (SUNSET_TIME+16, [Trigger("NIGHTSTARS")]),
    (SUNSET_TIME+37, [Trigger("AURORA")]),
    (SUNSET_TIME+47, [Trigger("AURORA", "spawn", 10)]),
    (SUNSET_TIME+56, [Trigger("AURORA", "end")]),
    (SUNSET_TIME+64, [Trigger("MOONRISE")]),
    (SUNSET_TIME+77, [Trigger("MOONRISE", "overlay", 3)]), # fade time
    (SUNSET_TIME+87, [Trigger("MOONRISE", "overlay")]),
    (SUNSET_TIME+87, [Trigger("MOONRISE", "end", 10)]),
    (SUNSET_TIME+87, [Trigger("NIGHTSTARS", "end", 10)]), #fadetime



    #(235, [Trigger("ripples", "end"), Trigger("BIRDS", 'set_action', 'rotate_camera')]),
    #(250, [Trigger("FOREST")]),  # Forest SoundsStarts
    #(260, [Trigger("SUNSET"), Trigger("BIRDS", "end")]),  # Sea Birds SoundsEnd #Waves SoundsEnd
    #(270, [Trigger("CONSTELLATION"), Trigger("FOREST", "end")]),  # Night Crickets and Star SoundsStart #Forest SoundsEnd
]


scene_data = {
    "STARS": (0, StarrySky, 150, 20, 0.1, 2.0), # max_stars, ramp_time, min_time, max_time
    "MORNINGSKY":(5, Fog, (0, 0, 255), 25), 
    "CLOUDSKY":(7, Fog, (0, 66, 128), 3),  
    "NIGHTSTARS": (0, StarrySky, 150, 10, 0.1, 2.0), # max_stars, ramp_time, min_time, max_time

    "AURORA": (5, Aurora, (66, 53), 2, 5), # middle, blob_duration, num_blobs

    "SUNRISE": (10, Sun, (-40, 51), 40, 0.3, 3, 2.0), #start, end, size, ripple_height, ripple_count, ripple_speed, duration
    "SUNSET": (29, Sun, (66, 51), 0, 0.3, 3, 2.0), #start, end, size, ripple_height, ripple_count, ripple_speed, duration

    "FOG": (12, Fog, (100, 100, 100), 10),

    "LIGHTNING_high": (15, Thunderstorm),
    "CLOUDS": (20, Clouds, MADRIX_SIZE, 4, 0.2, 0.50, 20), #size, cloud_size, initial_prob, final_prob, ramp_duration

    "RAINSMALL": (25, Raindrops, 1, 0.33, 75, 30), #drop_size, drop_duration, max_drops, ramp_time
    "RAINMID": (25, Raindrops, 1, 0.33, 30, 15), #drop_size, drop_duration, max_drops, ramp_time
    "RAINBIG": (25, Raindrops, 3, 0.50, 10, 5),
    "LIGHTNING_low": (25, Thunderstorm),
    'ripples': (28, Ripples),

    "WAVES": (50, Sea, 0.6, 0.25, 15), #wave_speed, beacon_speed, beacon_size

    "BIRDS": (60, Bird, pygame.Rect(57, 44, 16, 10)),


    "CONSTELLATION": (50, Constellation, 49, 29),
    "MOONRISE": (60, HSMoon, (66, 51), 7, 10), # position, size, fade_duration
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
    pygame.quit()

sys.exit()
