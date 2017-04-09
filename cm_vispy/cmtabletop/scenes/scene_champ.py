from .scene import Scene
from ..types.card import Card
from ..types.msg import Msg
from .. import global_vars as GV


class SceneChamp(Scene):
    im = None

    def __init__(self, actors, half):
        self.half = half
        Scene.__init__(self, actors)
        self.select = False
        for a in self.actors:
            a.surface = SceneChamp.im.copy()

    def draw(self, program):
        SceneChamp.im.get_tex_vertices(*self.get_coords(0))
        program['u_texture'] = SceneChamp.im.get_tex()
        program.bind(SceneChamp.im.get_vbo())
        program.draw('triangles')
        Scene.draw(self, program)

    def activate(self, active_half, pos):
        if active_half == self.half:
            if type(self.actors[pos]) == Card:
                pass
            else:
                return Msg.emptyToSelf(Msg.FLAG_CHAMP_EMPTY_SPOT, (self.half, -1), self.get_coords(0))

    def react_to(self, msg):
        if msg.rcv_half == self.half:
            if msg.flag == Msg.FLAG_HAND_TO_CHAMP:
                self._set_new_champ(msg.arg)

    def _set_new_champ(self, card):
        self.actors[0] = card
        x, y = self.get_coords(0)
        self.actors[0].slideTo(x, y)

    def get_coords(self, pos):
        xpos = float(GV.SCR_W - GV.CARD_W) * 0.5
        ypos = (0.01 + (1.0 - 0.01 * 2) * self.half) * GV.SCR_H - self.half * GV.CARD_H
        return xpos, ypos
