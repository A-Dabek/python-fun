import vispy
from vispy import gloo, app
from opengl.display import Display
import opengl.global_vars as GV
from opengl.collision import CollisionSystem as Collision
from opengl.collidables import Collidable, Ability


class Game(app.Canvas):
    # static fields

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(GV.SCR_W, GV.SCR_H))

        Display.init_display(*self.physical_size)

        self.actors = [
            Collidable(size=3, speed=0.5, x=100, y=100, color='red', behaviour_ai='key_controlled', movement_ai='key_controlled', ability=Ability(), health=100),
            Collidable(size=5, speed=0.1, x=200, y=200, color='blue', movement_ai='random', ability=Ability(), health=100)
        ]

        self.key_states = {
            'Left': False,
            'Up': False,
            'Down': False,
            'Right': False,
            'Q': False,
            'W': False,
            'A': False,
            'S': False,
            'D': False
        }

        Collidable.user_input = self.key_states

        self._timer = app.Timer(1.0 / GV.TEST_FPS, connect=self.update, start=True)
        self.show()

    def on_draw(self, event):

        gloo.clear()
        a_i = 0
        while a_i < len(self.actors):
            a = self.actors[a_i]
            if a.gone:
                del self.actors[a_i]
                continue
            #print(a._health)
            a_i += 1
            Display.draw_particle(a.surface)
            Collision.add(a)
            projectiles = a.move()
            if projectiles is not None:
                for aa in projectiles:
                    self.actors.append(aa)

        Collision.resolve()
        Collision.clear()

    def on_key_press(self, event):
        if self.key_states.get(event.key.name, None) is not None:
            self.key_states[event.key.name] = True

    def on_key_release(self, event):
        if self.key_states.get(event.key.name, None) is not None:
            self.key_states[event.key.name] = False

    def on_mouse_press(self, event):
        mx, my = event.pos

    def on_mouse_move(self, event):
        pass


if __name__ == '__main__':
    vispy.use('PyQt5', 'gl2')
    c = Game()
    c.measure_fps(10)
    app.run()
