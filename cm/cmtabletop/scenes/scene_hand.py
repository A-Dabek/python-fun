from .scene import Scene
from cm.cmtabletop.types.msg import Msg
from .. import screen
import pygame
from pygame import transform


class SceneHand(Scene):
    im = None

    def __init__(self, crystals, half):
        self.half = half
        Scene.__init__(self, crystals)
        self.select = -1
        self.budget = 0
        self.active = 0

    def _get_image(self, pos):
        clr = None
        flag = None
        if 0 > pos or pos >= len(self.actors):
            return SceneHand.im
        im_ret = self.actors[pos].im
        im_ret = transform.smoothscale(im_ret, (int(screen.card_w), int(screen.card_h)))
        if self.active != self.half or self.actors[pos].cost > self.budget:
            flag = pygame.BLEND_RGB_SUB
            clr = (70, 70, 70, 255)
        elif pos == self.select:
            flag = pygame.BLEND_RGB_ADD
            clr = (100, 100, 100, 255)
        if flag is not None and clr is not None:
            im_ret.fill(clr, None, flag)
        return im_ret

    def activate(self, active_half, pos):
        if active_half == self.half:
            if self.budget >= self.actors[pos].cost:
                self.select = pos
        pass

    def react_to(self, msg):
        if msg.flag == Msg.FLAG_SKIP:
            self.select = -1
            self.active = msg.rcv_half

        if self.half == msg.rcv_half:

            if msg.flag == Msg.FLAG_BOARD_EMPTY_SPOT:
                if self.select >= 0:
                    card = self.play_card()
                    return Msg.toSelf(Msg.FLAG_HAND_TO_BOARD, card, (self.half, -1), (msg.snd_x, msg.snd_y))

            if msg.flag == Msg.FLAG_CHAMP_EMPTY_SPOT:
                if self.select >= 0:
                    card = self.play_card()
                    return Msg.toSelf(Msg.FLAG_HAND_TO_CHAMP, card, (self.half, -1), (msg.snd_x, msg.snd_y))

            if msg.flag == Msg.FLAG_DECK_TO_HAND:
                    self.append_actor(msg.arg)

            if msg.flag == Msg.FLAG_CRYSTALS_SPARE:
                self.budget = msg.arg
        else:
            pass
        pass

    def play_card(self):
        card = self.actors[self.select]
        del self.actors[self.select]
        self.select = -1
        self.rearrange()
        return card

    def get_coords(self, pos):
        pos += 1
        xmargin = 0.01 * screen.bg_w + screen.card_w / 2
        xpos = (screen.bg_w - screen.card_w) / 2 + xmargin * (2 * (pos % 2) - 1)
        xpos += (screen.card_w / 2 * ((pos + 1) / 2)) * (2 * (pos % 2) - 1)
        ypos = (0.01 + (1.0 - 0.01 * 2) * self.half) * screen.bg_h - self.half * screen.card_h
        return xpos, ypos
