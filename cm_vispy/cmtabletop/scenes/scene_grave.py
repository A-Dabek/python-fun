from .scene import Scene
from cm_vispy.cmtabletop.types.actor import Actor
from cm_vispy.cmtabletop.types.msg import Msg
from .. import global_vars as GV
from pygame import transform
import math


class SceneGrave(Scene):
    im = None
    d = 0

    def __init__(self, cards, half):
        self.half = half
        Scene.__init__(self, cards)
        SceneGrave.d = math.ceil(math.sqrt(GV.CARD_W ** 2 + GV.CARD_H ** 2))

    def _get_surface(self, pos):
        if 0 <= pos < len(self.actors):
            return transform.rotate(self.actors[pos].im, self.actors[pos].sAngle)
        return SceneGrave.im

    def react_to(self, msg):
        if self.half == msg.rcv_half:
            if msg.flag == Msg.BOARD_TO_GRAVE:
                import random
                self.append_actor(Actor(SceneGrave.im.copy(), sx=msg.snd_x, sy=msg.snd_y, angle=random.randint(1, 360)))
        else:
            pass
        pass

    def get_coords(self, pos):
        surf = transform.rotate(self.actors[pos].im.copy(), self.actors[pos].dAngle)
        xpos = (SceneGrave.d - surf.get_width()) * 0.5
        ypos = (SceneGrave.d - surf.get_height()) + self.half * (GV.SCR_H - GV.CARD_H)
        return xpos, ypos
