from .scene import Scene
from cm.cmtabletop.types.actor import Actor
from cm.cmtabletop.types.msg import Msg
from .. import screen


class SceneCrystal(Scene):

    def activate(self, active_half, pos):
        pass

    im = None

    def __init__(self, crystals, half):
        self.half = half
        self.spare = 0
        Scene.__init__(self, crystals)

    def _get_image(self, pos):
        im_ret = SceneCrystal.im.copy()
        import pygame
        if pos >= self.spare:
            im_ret.fill((100, 100, 100, 255), None, pygame.BLEND_RGB_SUB)
        return im_ret

    def react_to(self, msg):
        if msg.rcv_half == self.half:
            if msg.flag == Msg.FLAG_HAND_TO_BOARD:
                self.spare -= msg.arg.cost
                return Msg.toSelf(Msg.FLAG_CRYSTALS_SPARE, self.spare, (self.half, -1))

            if msg.flag == Msg.FLAG_HAND_TO_CHAMP:
                self.spare -= msg.arg.cost
                return Msg.toSelf(Msg.FLAG_CRYSTALS_SPARE, self.spare, (self.half, -1))

            if msg.flag == Msg.FLAG_SKIP:
                x, y = self.get_coords(0)
                self.append_actor(Actor(self.im.copy(), sx=x, sy=y))
                self.refresh()
                return Msg.toSelf(Msg.FLAG_CRYSTALS_SPARE, self.spare, (self.half, -1))
        else:
            pass
        pass

    def refresh(self):
        self.spare = len(self.actors)

    def get_coords(self, pos):
        xmargin = screen.bg_w * 0.5 - SceneCrystal.im.get_width() * 0.25
        xpos = xmargin - float(SceneCrystal.im.get_width() * len(self.actors)) * 0.5 + SceneCrystal.im.get_width() * pos
        ypos = (0.01 + (1.0 - 0.01 * 2) * self.half) * screen.bg_h - (2 * self.half - 1) * screen.card_h \
               - self.half * SceneCrystal.im.get_height()
        return xpos, ypos
