from .actor import Actor
from pygame import image, transform
from .. import screen


class Animation(Actor):
    TYPE_THROW = 0
    TYPE_HOVER = 1
    TYPE_TEXT_HOVER = 2
    LIFE_ONCE = 0
    LIFE_REAPEAT = 1
    icon_path = '/root/PycharmProjects/equations/cm/features/'

    def __init__(self, im, type, life_type=LIFE_ONCE, with_text=""):
        Actor.__init__(self, self.load_icon(im, with_text=with_text))
        self.type = type
        self.life = life_type
        self.speed = 30

    def load_icon(self, name, with_text=""):
        im = image.load(Animation.icon_path + name + '.png').convert()

        if with_text is not '':
            from pygame import font
            font = font.SysFont("impact", int(im.get_height() / 2))
            label = font.render(with_text, True, (255, 255, 255))
            im.blit(label, (im.get_width() - label.get_width(),
                                 im.get_height() - label.get_height()))

        return transform.smoothscale(im, (int(screen.card_w/3), int(screen.card_h/3)))

    def set_speed(self, speed):
        self.speed = speed

    def draw(self, onto):
        onto.blit(self.im, (self.X, self.Y))

    def progress(self):
            self.X += self.aX
            self.Y += self.aY

    def get_im(self):
        from pygame import transform
        if self.type == Animation.TYPE_THROW:
            self.angle += 15
            return transform.rotate(self.im, self.angle)
        return self.im
