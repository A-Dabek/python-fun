from .scene import Scene
from ..types.card import Card
from ..types.msg import Msg
from .. import screen
from pygame import transform


class SceneChamp(Scene):
    im = None

    def __init__(self, crystals, half):
        self.half = half
        Scene.__init__(self, crystals)
        self.select = False

    def _get_image(self, pos):
        if type(self.actors[pos]) == Card:
            im_ret = self.actors[pos].im.copy()
            im_ret = transform.smoothscale(im_ret, (int(screen.card_w), int(screen.card_h)))
            self.actors[pos].show_board_state(im_ret)
            return im_ret
        else:
            return SceneChamp.im

    def draw(self, onto):
        onto.blit(SceneChamp.im, self.get_coords(0))
        Scene.draw(self, onto)

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
        xpos = float(screen.bg_w - screen.card_w) * 0.5
        ypos = (0.01 + (1.0 - 0.01 * 2) * self.half) * screen.bg_h - self.half * screen.card_h
        return xpos, ypos
