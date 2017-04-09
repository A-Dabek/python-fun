from .scene import Scene
from ..types.msg import Msg
from ..types.animation import Animation
from .. import screen


class SceneAnimation(Scene):
    def __init__(self):
        Scene.__init__(self, 0)
        pass

    def react_to(self, msg):
        if msg.flag == Msg.FLAG_BOARD_CREATURE_ACTION:
            anim = Animation(msg.arg[0], Animation.TYPE_HOVER, with_text=str(msg.arg[1]))
            self.actors.append(anim)
            anim.set_speed(30)
            x, y = self.get_coords(len(self.actors) - 1, msg.rcv_x, msg.rcv_y)
            anim.moveTo(x, y)
            anim.slideTo(x, msg.rcv_y)
        pass

    def update(self):
        Scene.update(self)
        while len(self.actors) > 0 and not self.actors[0].moving and not self.actors[0].life == Animation.LIFE_REAPEAT:
            del self.actors[0]

    def activate(self, active_half, pos):
        pass

    def get_coords(self, pos, x=0, y=0):
        X = x + screen.card_w / 2 - self.actors[pos].im.get_width() / 2
        Y = y + screen.card_h / 2 - self.actors[pos].im.get_height() / 2
        return X, Y

    def _get_image(self, pos):
        if 0 <= pos < len(self.actors):
            return self.actors[pos].im
        return None

    def playing(self):
        return len(self.actors) > 0
