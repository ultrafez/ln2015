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
     90 * FPS: [Trigger("CLOUDS", "grey", (FPS * 20,))],
    100 * FPS: [
        Trigger("LIGHTNING"), # Fork and Sheet Lightning SoundsStart
        Trigger("LIGHTNING", "add_sheet", (left_arm,)),
        Trigger("LIGHTNING", "add_sheet", (right_arm,)),
        Trigger("LIGHTNING", "add_sheet", (top_arm,))
    ],
    110 * FPS: [Trigger("RAIN")],  # Rain SoundsStart
    114 * FPS: [
        Trigger("LIGHTNING",  "add_fork", ((MADRIX_X, MADRIX_Y), (130, 55), (0, 55))),
        Trigger("LIGHTNING",  "add_fork", ((MADRIX_X, MADRIX_Y), (75, 0), (75, 70)))
    ],  # Fork
    140 * FPS: [Trigger("LIGHTNING", "end")],  # Lightning SoundsEnd
    150 * FPS: [Trigger("WAVES")],  # Wave and Ambient SoundsStart
    180 * FPS: [Trigger("CLOUDS", "end", (5 * FPS,)), Trigger("RAIN", "end")],  # Clouds FadeEnd #Rain SoundsEnd
    190 * FPS: [Trigger("WAVES", "change", (5, 5.0, 2 * FPS))],
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


scene_data = {
    "STARS": (StarrySky, ((MADRIX_X, MADRIX_Y),)),
    "HS_SPIN": (HSMoon, (1, 39, 4,-45, 0)),
    "SUNRISE": (RisingSun, ((66, 70), (66, 35), 10, FPS * 2, FPS)),
    "CLOUDS": (Clouds, ((MADRIX_X, MADRIX_Y), 4, 0.1, 0.25, 20 * FPS)),
    "LIGHTNING": (Thunderstorm, ()),
    "RAIN": (Raindrops, ((MADRIX_X, MADRIX_Y),)),
    "MOONRISE": (HSMoon, ()),
    "WAVES": (Sea, ((MADRIX_X, MADRIX_Y), 2, 3.0)),
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
    args = parser.parse_args()

    print(args)

    clean_images()

    LN2015 = Player('objects', MADRIX_X, MADRIX_Y, fps=FPS, display_scale=8,  args=args)

    for key, trig in key_triggers.items():
        LN2015.set_key_triggers(key, trig)

    for scene, data in scene_data.items():
        LN2015.load_scene(scene, data)

    for ticks, events in EVENT_TIMING.items():
        LN2015.load_timed_event(ticks, events)

    alive = True
    while alive:
        alive = LN2015.run()

        if 'windows' in platform.platform().lower():
            ffmpeg_exe = 'C:\\Users\\admin\\Desktop\\ffmpeg-20150921-git-74e4948-win64-static\\bin\\ffmpeg.exe'
        else:
            ffmpeg_exe = 'ffmpeg'

        if LN2015.ticks > TOTAL_TIME * FPS:
            alive = False
    LN2015.export_video(MADRIX_X*8, MADRIX_Y*8, ffmpeg_exe)
    pygame.quit()

sys.exit()
