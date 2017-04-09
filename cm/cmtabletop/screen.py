import pygame

ratio = (1600, 900)
scale = 0.6
w = int(ratio[0] * scale)
h = int(ratio[1] * scale)
card_w = 0
card_h = 0
cr_w = 0
cr_h = 0
bg_w = 0
bg_h = 0
global surf


def init():
    global surf
    pygame.init()
    surf = pygame.display.set_mode((w, h))
    pygame.display.set_caption('Tabletop simulator')
