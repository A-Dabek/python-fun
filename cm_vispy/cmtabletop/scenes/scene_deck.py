from .scene import Scene
from cm_vispy.cmtabletop.types.card import Card
from cm_vispy.cmtabletop.types.msg import Msg
from .. import global_vars as GV


class SceneDeck(Scene):
    im = None

    def __init__(self, cards, half):
        self.half = half
        Scene.__init__(self, cards)
        for a in self.actors:
            a.surface = SceneDeck.im.copy()

    def add_cards_list(self, card_list):
        self.actors = [Card(i) for i in card_list]
        self.arrange()
        #for a in self.actors:
        #    a.surface = SceneDeck.im.copy()

    def activate(self, active_phase, pos):
        if active_phase == self.half:
            return Msg.emptyToOpposite(Msg.FLAG_SKIP, (self.half, -1))
        pass

    def react_to(self, msg):
        if self.half == msg.rcv_half:

            if msg.flag == Msg.FLAG_SKIP:
                return Msg.emptyToSelf(Msg.FLAG_DRAW, (self.half, -1))

            if msg.flag == Msg.FLAG_DRAW:
                card = self.get_card_from_top(and_remove=True)
                if card is not None:
                    return Msg.toSelf(Msg.FLAG_DECK_TO_HAND, card, (self.half, -1))
        else:
            pass
        pass

    def get_coords(self, pos):
        xpos = (GV.SCR_W - GV.CARD_W * (1.05 + 0.025 * pos))
        ypos = (0.01 + (1.0 - 0.01 * 2) * self.half) * GV.SCR_H - self.half * GV.CARD_H
        return xpos, ypos

    def get_card_from_top(self, and_remove=False):
        if len(list(self.actors)) > 0:
            card = self.actors[0]
            if and_remove:
                del self.actors[0]
            return card
        return None
