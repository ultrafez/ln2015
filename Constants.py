__author__ = 'ajtag'

import pygame


white = 255, 255, 255, 0xff
black = 0, 0, 0, 0xff
red = 255, 0, 0, 0xff
green = 0, 255, 0, 0xff
blue = 0, 0, 255, 0xff
dark_grey = 0x30, 0x30, 0x30, 0xff
transparent = 0xff, 0xff, 0xff, 0xff


bubbleroof = pygame.Rect((50, 34), (28, 33))
island = pygame.Rect((0, 41), (12, 7))
left_outer_arm = pygame.Rect((16, 42), (18, 8))
left_inner_arm = pygame.Rect((33, 37), (16, 13))
top_outer_arm = pygame.Rect((61, 1), (0, 18))
top_inner_arm = pygame.Rect((60, 18), (9, 18))
right_inner_arm = pygame.Rect((77, 40), (21, 12))
right_outer_arm = pygame.Rect((97, 40), (28, 12))