from cm_vispy.cmtabletop.types.actor import Actor
import abc


class Scene:
    def __init__(self, actor_amount):
        self.actors = [Actor(None) for _ in range(actor_amount)]
        self.arrange()

    @abc.abstractmethod
    def react_to(self, msg):
        pass

    @abc.abstractmethod
    def activate(self, active_half, pos):
        pass

    @abc.abstractmethod
    def get_coords(self, pos):
        pass

    def draw_new2(self, display):
        for i in range(len(self.actors)):
            surf = self.get_surface(i)
            if surf is not None:
                display.add(surf)

    def draw(self, program):
        for i in range(len(self.actors)):
            surf = self.get_surface(i)
            if surf is not None:
                program['u_texture'] = surf.get_tex()
                program.bind(surf.get_vbo())
                program.draw('triangles')

    def get_surface(self, pos):
        if 0 <= pos < len(self.actors):
            return self.actors[pos].surface
        return None

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
            x, y = self.actors[i].get_coords()
            if self.actors[i].surface is None:
                continue
            w, h = self.actors[i].surface.get_shape()
            if x < mx < x + w and y < my < y + h:
                return i
        return False
