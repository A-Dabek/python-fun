from cm.cmtabletop.types.actor import Actor
import abc


class Scene:
    active_scene = (-1, None)

    def __init__(self, actor_amount):
        self.actors = actor_amount * [None]
        self.upload_actors()
        self.arrange()

    def upload_actors(self):
        self.actors = [Actor(self._get_image(-1)) for _ in self.actors]
        print(self.actors)

    @abc.abstractmethod
    def react_to(self, msg):
        pass

    @abc.abstractmethod
    def activate(self, active_half, pos):
        pass

    @abc.abstractmethod
    def _get_image(self, pos):
        pass

    @abc.abstractmethod
    def get_coords(self, pos):
        pass

    def draw(self, onto):
        for i in range(len(self.actors)):
            im, (x, y) = self.get_blit_data(i)
            if im is not None:
                onto.blit(im, (x, y))

    def get_blit_data(self, pos):
        if 0 <= pos < len(self.actors):
            return self._get_image(pos), self.actors[pos].getCoords()
        return None, (0, 0)

    def append_actor(self, actor):
        # x, y = self.get_coords(len(self.actors))
        # actor.slideTo(x, y)
        self.actors.append(actor)
        self.rearrange()

    def update(self):
        for a in self.actors:
            a.move()

    def arrange(self):
        for i in range(len(self.actors)):
            x, y = self.get_coords(i)
            self.actors[i].moveTo(x, y)

    def rearrange(self):
        for i in range(len(self.actors)):
            x, y = self.get_coords(i)
            self.actors[i].slideTo(x, y)

    def listen(self, mx, my):
        for i in range(len(self.actors) - 1, -1, -1):
            x, y = self.actors[i].getCoords()
            if x < mx < x + self._get_image(-1).get_width() \
                    and y < my < y + self._get_image(-1).get_height():
                return i
        return False
