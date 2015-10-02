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


__author__ = 'ajtag'

logging.basicConfig()

FPS = 24
SCALE = 8
TOTAL_TIME = 360

key_triggers = {
    pygame.K_MINUS:Trigger("LIGHTNING", "add_sheet", (left_outer_arm,)),
    pygame.K_EQUALS: Trigger("LIGHTNING", "add_fork", ((MADRIX_X, MADRIX_Y), (130, 55), (0, 55))),
    pygame.K_q: Trigger("STARS"),
    pygame.K_a: Trigger("SUNRISE"),
    pygame.K_w: Trigger("STARS", "fade"),
    pygame.K_e: Trigger("STARS", "end"),
    pygame.K_z: Trigger("CLOUDS"),
    pygame.K_d: Trigger("LIGHTNING"),
    pygame.K_c: Trigger("RAIN"),
    pygame.K_f: Trigger("LIGHTNING", "end"),
    pygame.K_g: Trigger("WAVES"),
    pygame.K_v: Trigger("RAIN", "end"),

    pygame.K_y: Trigger("BIRDS"),
    pygame.K_1: Trigger("BIRDS", "set_action", ('bob', )),
    pygame.K_2: Trigger("BIRDS", "set_action", ('takeoff', )),
    pygame.K_3: Trigger("BIRDS", "set_action", ('rotate_camera', )),

    pygame.K_h: Trigger("WAVES", "end"),
    pygame.K_b: Trigger("FOREST"),
    pygame.K_u: Trigger("BIRDS", "end"),
    pygame.K_n: Trigger("FOREST", "end"),
    pygame.K_j: Trigger("SUNSET"),
    pygame.K_i: Trigger("CONSTELLATION"),
    pygame.K_k: Trigger("SUNSET", "end"),
    pygame.K_p: Trigger("NORTHERNLIGHTS"),
    pygame.K_LEFTBRACKET: Trigger("NORTHERNLIGHTS", "end"),
    pygame.K_m: Trigger("MOONRISE"),
    pygame.K_COMMA: Trigger("MOONRISE", "end"),
    pygame.K_o: Trigger("CONSTELLATION", "end")
}

EVENT_TIMING = [
    (  0, [Trigger("STARS"), Trigger("HS_SPIN")]),  # Star Sounds and CricketsStart
    ( 30, [Trigger("SUNRISE"), Trigger("STARS", "fade"), Trigger("HS_SPIN", "end")]),  # Bird Song Dawn ChorusStart Stars and Crickets FadeEnd
    ( 40, [Trigger("STARS", "end")]),  # Star Sounds and CricketsEnd
    ( 50, Trigger("SUNRISE", "end", (5,))),
    ( 60, [Trigger("CLOUDS")]),  # Clouds and Wind SoundsStart
    ( 90, [Trigger("CLOUDS", "grey", (0.4, 20))]),
    (100, [
        Trigger("LIGHTNING"), # Fork and Sheet Lightning SoundsStart
        Trigger("LIGHTNING", "add_sheet", (left_arm,)),
        Trigger("LIGHTNING", "add_sheet", (right_arm,)),
        Trigger("LIGHTNING", "add_sheet", (top_arm,))
    ]),
    (110, [Trigger("RAIN")]),  # Rain SoundsStart
    (114, [
        Trigger("LIGHTNING",  "add_fork", ((MADRIX_X, MADRIX_Y), (130, 55), (0, 55))),
        Trigger("LIGHTNING",  "add_fork", ((MADRIX_X, MADRIX_Y), (75, 0), (75, 70)))
    ]),  # Fork
    (140, [Trigger("LIGHTNING", "end")]),  # Lightning SoundsEnd
    (150, [Trigger("WAVES")]),  # Wave and Ambient SoundsStart
    (180, [Trigger("CLOUDS", "end", (5,)), Trigger("RAIN", "end")]),  # Clouds FadeEnd #Rain SoundsEnd
    (190, [Trigger("WAVES", "change", (5, 5.0, 2 * FPS))]),
    (200, [Trigger("WAVES", "beacon", (5, ))]),  # Waves Ring Bouys to MakeSounds
    (220, [Trigger("BIRDS"), Trigger("BIRDS", 'set_action', ('bob', ))]),  # Sea Birds SoundsStart
    (225, [Trigger("BIRDS", 'set_action', ('takeoff',))]),
    (235, [Trigger("BIRDS", 'set_action', ('rotate_camera',))]),

    (240, [Trigger("WAVES", "beacon", (0,))]),  # Stop beacon respawn
    (250, [Trigger("FOREST")]),  # Forest SoundsStarts
    (260, [Trigger("WAVES", "end"), Trigger("SUNSET"), Trigger("BIRDS", "end")]),  # Sea Birds SoundsEnd #Waves SoundsEnd
    (270, [Trigger("CONSTELLATION"), Trigger("FOREST", "end")]),  # Night Crickets and Star SoundsStart #Forest SoundsEnd
    (280, [Trigger("SUNSET", "end")]),  #
    (290, [Trigger("NORTHERNLIGHTS")]),  # Northern Lights Sounds Start (Ambient Sine Bass Notes?)
    (310, [Trigger("NORTHERNLIGHTS", "end")]),  # Northern Lights SoundsEnd
    (300, [Trigger("MOONRISE")]),  #
    (320, [Trigger("MOONRISE", "end"), Trigger("CONSTELLATION", "end")]),  #
]


scene_data = {
    "STARS": (StarrySky, ((MADRIX_X, MADRIX_Y),)),
    #"HS_SPIN": (HSMoon, ( pygame.Rect(5, 30, 10, 10), -45, -3)),
    #"HS_SPIN": (HSMoon, ( pygame.Rect(0, 40, 25, 25), 0, 0-3)),
    "SUNRISE": (RisingSun, ((66, 78), (66, 53), 8, 10)),
    "CLOUDS": (Clouds, ((MADRIX_X, MADRIX_Y), 4, 0.1, 0.25, 20)),
    "LIGHTNING": (Thunderstorm, ()),
    "RAIN": (Raindrops, ((MADRIX_X, MADRIX_Y),)),
    "CONSTELLATION": (Constellation, (49, 29)),
    "MOONRISE": (HSMoon, ()),
    "WAVES": (Sea, ((MADRIX_X, MADRIX_Y), 2, 3.0)),
    "BIRDS": (Bird, ((bubbleroof,))),
}


if __name__ == "__main__":

    random.seed('correcthorsebatterystaple')

    logging.getLogger().setLevel(logging.INFO)
    pygame.init()

    parser = argparse.ArgumentParser()
    parser.add_argument("--warp", type=float, default=0.0)
    parser.add_argument("--no-mask", action="store_false", dest="mask")
    parser.add_argument("--no_images", action="store_false", dest="save_images")
    parser.add_argument("--save-video", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--avconv", action="store_true")
    args = parser.parse_args()

    print(args)

    clean_images()

    LN2015 = Player('objects', MADRIX_X, MADRIX_Y, fps=FPS, display_scale=8,  args=args)

    for key, trig in key_triggers.items():
        LN2015.set_key_triggers(key, trig)

    for scene, data in scene_data.items():
        LN2015.load_scene(scene, data)

    for ticks, events in EVENT_TIMING:
        LN2015.load_timed_event(ticks, events)

    #LN2015.load_sprite('Bird', Constellation(50, 34))

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
    LN2015.export_video(MADRIX_X, MADRIX_Y, ffmpeg_exe)
    pygame.quit()

sys.exit()
