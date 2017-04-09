from .scene import Scene
from cm_vispy.cmtabletop.types.actor import Actor
from cm_vispy.cmtabletop.types.msg import Msg
from .. import global_vars as GV


class SceneCrystal(Scene):

    def activate(self, active_half, pos):
        pass

    im = None

    def __init__(self, crystals, half):
        self.half = half
        self.spare = 0
        Scene.__init__(self, crystals)
        for a in self.actors:
            a.surface = SceneCrystal.im.copy()

    def _get_surface(self, pos):
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
                self.append_actor(Actor(SceneCrystal.im.copy(), sx=x, sy=y))
                self.refresh()
                return Msg.toSelf(Msg.FLAG_CRYSTALS_SPARE, self.spare, (self.half, -1))
        else:
            pass
        pass

    def refresh(self):
        self.spare = len(self.actors)

    def get_coords(self, pos):
        xmargin = GV.SCR_W * 0.5 - GV.CR_W * 0.25
        xpos = xmargin - float(GV.CR_W * len(self.actors)) * 0.5 + GV.CR_W * pos
        ypos = (0.01 + (1.0 - 0.01 * 2) * self.half) * GV.SCR_H - (2 * self.half - 1) * GV.CARD_H \
               - self.half * GV.CR_H
        return xpos, ypos
