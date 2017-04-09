import pygame
import sys
from pygame.locals import *

from cm.cmtabletop import duel, screen


def terminate():
    pygame.quit()
    sys.exit()


screen.init()
card_names = ['Edge', 'Darkblade', 'Isickle', 'Kurtey', 'Precious', 'Sniperoo', 'Tridentite', 'Kurtey', 'Precious', 'Tridentite']
card_names2 = list(card_names)
from random import shuffle
shuffle(card_names2)
duel.createGame(card_names, card_names2)
# main loop
from pygame.time import Clock
fps = Clock()

while True:
    # print(fps.get_fps())
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        elif event.type == MOUSEBUTTONDOWN:
            duel.acceptClick(event.dict.get('pos'))
    duel.drawGameState(screen.surf)
    pygame.display.update()
    fps.tick(45)
