#! /usr/bin/env python3
import sys
sys.path.append('TrinRoofPlayer')

from ln_objects import *
import pygame
from TrinRoofPlayer.Renderer import Player, clean_images, Trigger
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

EVENT_TIMING = [
    (  0, [Trigger("STARS")]),
    ( 30, Trigger("MORNINGSKY")),
    ( 30, [Trigger("SUNRISE"), Trigger("SUNRISE", "move", (66, 51), 7, 30)]),
    ( 38, [Trigger("STARS", "end", 5)]),  #fadetime
    ( 53, [Trigger("CLOUDS")]),
    ( 65, Trigger("CLOUDSKY")),
    ( 75, Trigger("MORNINGSKY", "end", 5)),
    ( 75, Trigger("SUNRISE", "move", None, 0, 10)), # newpos, newsize, duration
    ( 75, Trigger("SUNRISE", "end", 10)),  # fadetime
    ( 75, Trigger("CLOUDSKY", "end", 15)),
    ( 85, [Trigger("CLOUDS", "grey", 0.6, 10)]),
    ( 85, Trigger("FOG")),


    #FIRST LIGHTNING STRIKES
    ( 90, [Trigger("LIGHTNING_high"), Trigger("LIGHTNING_high", 'incoming', 10)]),  # start lightning incoming
    (109, [Trigger("LIGHTNING_low"), Trigger("LIGHTNING_low", 'big_hit')]),
    
    #Trigger("ripples")
    (140, [Trigger("LIGHTNING_low", "end"), Trigger("LIGHTNING_high", "outgoing", 10)]),  # stop main storm and fade  outer storm
    (135, [Trigger("RAIN")]),  # start rain and ripples
    (140, [Trigger("LIGHTNING_high", "end")]),  # Lightning End

    #FIRST WAVE
    (150, [Trigger("WAVES"), Trigger("WAVES", "spawn", 20, 180, 1, 3)]),  # width, angle, num_waves, interval

    #END RAIN CLOUDS
    (153.75, [Trigger("RAIN", "end", 2)]),
    (154.75, Trigger("CLOUDS", "end", 2)), # fadetime
    (154.75, Trigger("FOG", "end", 2)), # fadetime

    #WAVES AND BEACONS
    (155, [Trigger("WAVES", "spawn", 15, 180, 1, 3)]),
    (160, [Trigger("WAVES", "spawn", 10, 180, 1, 3)]),
    (162, [Trigger("WAVES", "beacon", 1)]),  # number buoys
    (162, [Trigger("WAVES", "spawn", 6, 180, 2, 3)]),
    (169, [Trigger("WAVES", "beacon", 3)]),  # number buoys
    (167, [Trigger("WAVES", "spawn", 4, 180, 10, 2)]),
    (185, [Trigger("WAVES", "spawn", 4, 180, 3, 3)]),
    (185, [Trigger("WAVES", "beacon", 1)]),  # number buoys
    (192, [Trigger("WAVES", "beacon", 0)]),  # number buoys

    #SUNSET
    (196, [Trigger("SUNSET"), Trigger("SUNSET", "move", None, 7, 5)]),
    (202, [Trigger("SUNSET", "move", (66, 110), 40, 30)]), # newpos, newsize, duration
    (232, [Trigger("SUNSET", "move", None, 0, 10)]), # newpos, newsize, duration
    (232, [Trigger("SUNSET", "end", 10)]), # fadetime

    #NIGHTSKY
    (217, [Trigger("NIGHTSTARS")]),
    (235, [Trigger("AURORA")]),
    (245, [Trigger("AURORA", "spawn", 10)]),
    (260, [Trigger("AURORA", "end")]),
    (270, [Trigger("MOONRISE")]),
    (285, [Trigger("MOONRISE", "overlay", 3)]), # fade time
    (295, [Trigger("MOONRISE", "overlay")]),
    (305, [Trigger("MOONRISE", "end", 10)]),
    (305, [Trigger("NIGHTSTARS", "end", 10)]), #fadetime



    #(220, [Trigger("BIRDS"), Trigger("BIRDS", 'set_action', 'bob')]),  # Sea Birds SoundsStart
    #(225, [Trigger("BIRDS", 'set_action', 'takeoff'), Trigger("ripples", 'set_action', 'takeoff2'),]),
    #(235, [Trigger("ripples", "end"), Trigger("BIRDS", 'set_action', 'rotate_camera')]),
    #(250, [Trigger("FOREST")]),  # Forest SoundsStarts
    #(260, [Trigger("SUNSET"), Trigger("BIRDS", "end")]),  # Sea Birds SoundsEnd #Waves SoundsEnd
    #(270, [Trigger("CONSTELLATION"), Trigger("FOREST", "end")]),  # Night Crickets and Star SoundsStart #Forest SoundsEnd
]


scene_data = {
    "STARS": (0, StarrySky, 60, 20, 0.2, 2.0), # max_stars, ramp_time, min_time, max_time
    "MORNINGSKY":(5, Fog, (119, 181, 254), 25), 
    "CLOUDSKY":(7, Fog, (0, 66, 128), 3),  
    "SUNRISE": (10, Sun, (66, 90), 20, 0.3, 3, 2.0), #start, end, size, ripple_height, ripple_count, ripple_speed, duration


    "FOG":(12, Fog, (100, 100, 100), 10),
    "LIGHTNING_high": (15, Thunderstorm),
    "CLOUDS": (20, Clouds, MADRIX_SIZE, 4, 0.2, 0.50, 20), #size, cloud_size, initial_prob, final_prob, ramp_duration
    "LIGHTNING_low": (25, Thunderstorm),

    "RAIN": (25, Raindrops, 3, 0.5, 25, 15), #drop_size, drop_duration, max_drops, ramp_time
    "BIRDS": (41, Bird, bubbleroof),
    "CONSTELLATION": (50, Constellation, 49, 29),
    "MOONRISE": (60, HSMoon, (66, 51), 7, 10), # position, size, fade_duration
    "WAVES": (70, Sea, 0.6, 0.5, 10), #wave_speed, beacon_speed, beacon_size
    "AURORA": (5, Aurora, (66, 53), 2, 5), # middle, blob_duration, num_blobs
    "SUNSET": (10, Sun, (66, 51), 0, 0.3, 3, 2.0), #start, end, size, ripple_height, ripple_count, ripple_speed, duration
    "NIGHTSTARS": (0, StarrySky, 60, 10, 0.2, 2.0), # max_stars, ramp_time, min_time, max_time
    'ripples': (100, Ripples, MADRIX_SIZE)
}


if __name__ == "__main__":

    random.seed('correcthorsebatterystaple')

    logging.getLogger().setLevel(logging.INFO)
    pygame.init()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--warp", type=float, default=-1.0)
    parser.add_argument("--no-mask", action="store_false", dest="mask")
    parser.add_argument("--image-format", default="png")
    parser.add_argument("--no-images", action="store_const", dest="image_format", const=None)
    parser.add_argument("--save-video", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--avconv", action="store_true")
    parser.add_argument("--random-seed", type=str, default="LN2015")
    parser.add_argument("--sparse", type=int, default=2)
    parser.add_argument("--solid", dest='sparse', action="store_const", const=0)
    parser.add_argument("--pause", action="store_true")
    parser.add_argument("--scale", type=int, default=8)
    parser.add_argument("--export-display", action="store_true")
    args = parser.parse_args()

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
