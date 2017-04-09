import random
from .surface import SurfaceList
from .movement import Movement
from .ieffects import Effect
from .. import global_vars as GV


class Collidable:
    _speed_limit = 10
    _AIs = ('straight', 'random', 'key_controlled')
    _collision = ('collide', 'pass', 'explode')
    _passives = ('',)
    user_input = {}

    def __init__(self, health=1., damage=1., size=1., size_per_unit=10,
                 color='black', collision_size=1.0, x=0, y=0, speed=0.5,
                 movement_ai='random', behaviour_ai='idle', collidable=True, ability=None, passive=None):
        if health < 0:
            health = 1
        if damage < 0:
            damage = 1
        if size < 0:
            size = 1
        self.health = health
        self._health = health
        self._damage = damage
        self._size = size

        self.collidable = collidable

        if movement_ai not in Collidable._AIs:
            movement_ai = Collidable._AIs[0]
        if movement_ai == 'random':
            self._AI_move = self.move_random
        elif movement_ai == 'key_controlled':
            self._AI_move = self.move_user
        else:
            self._AI_move = self.move_empty

        if behaviour_ai == 'key_controlled':
            self._AI_action = self.shot_user
        else:
            self._AI_action = self.shot

        w = size_per_unit * size
        self._col_w = w * collision_size
        self._surface = SurfaceList(amount=1, width=w, height=w, color=color)

        speed *= Collidable._speed_limit
        if speed < 0:
            speed = 0
        elif speed > Collidable._speed_limit:
            speed = Collidable._speed_limit
        self._movement = Movement(sx=x, sy=y, speed=speed * GV.FPS / GV.TEST_FPS)

        if ability is not None:
            ability.caster = self
        self._ability = ability

        if passive not in Collidable._passives:
            passive = Collidable._passives[0]
        self._passive = passive

        self._effects = []

    @property
    def alive(self):
        return self._health > 0

    @property
    def gone(self):
        return self._health is None

    @property
    def acceleration(self):
        return self._movement.aX, self._movement.aY

    @property
    def centerpoint(self):
        return self._movement.X, self._movement.Y

    @property
    def surface(self):
        return self._surface

    @property
    def shape(self):
        return self._surface.shape

    @property
    def collision_rect(self):
        w, h = self.shape
        return self._movement.X - w // 2, self._movement.Y - h // 2, w, h

    def add_effects(self, *efx):
        self._effects.extend(efx)

    def collision_reacts(self):
        cax, cay = self.acceleration
        return [Effect(name='strike', duration=0, damage=1),
                Effect(name='knockback', duration=cax, damage=cay)]

    def to_position(self, x, y):
        self._movement.slideTo(x, y)

    def by_direction(self, x, y):
        self._movement.fly(x, y)

    def move(self):
        ret = []

        # actor passive effects
        e_iter = 0
        while e_iter < len(self._effects):
            if self._effects[e_iter].affect(self) == 0:
                del self._effects[e_iter]
                continue
            e_iter += 1

        if self._health is None or self.health == 0:
            return ret

        # actor condition check
        if self._health <= 0:
            self.collidable = False
            self.health = 0
            self._effects.append(Effect(name='dim', duration=2.0, damage=0.0))

        # movement and action taking
        if self._AI_move():
            ret = self._AI_action()
        self._movement.move()

        # ability handle
        if self._ability is not None:
            self._ability.cooldown()

        # translation
        w, h = self.shape
        self._surface[(0, 'translate')] = self._movement.X - w // 2, self._movement.Y - h // 2
        return ret

    def shot(self):
        print('it goes')
        if self._ability is None:
            print('it none')
            return None
        x, y = self.centerpoint

        print('fire')
        return self._ability.fire(0, 1)

    def shot_user(self):
        if self._ability is None:
            return None
        dx, dy = 0, 0
        if Collidable.user_input['W']:
            dy = -1
        if Collidable.user_input['A']:
            dx = -1
        if Collidable.user_input['S']:
            dy = 1
        if Collidable.user_input['D']:
            dx = 1
        if dx == dy == 0:
            return []
        return self._ability.fire(dx, dy)

    def move_empty(self):
        return False

    def move_random(self):
        if not self._movement.moving:
            dX = random.randint(0, GV.SCR_W)
            dY = random.randint(0, GV.SCR_H)
            self._movement.slideTo(dX, dY)
        if self._ability is not None:
            return not self._ability.on_cooldown()
        return False

    def move_user(self):
        dx, dy, ret = 0, 0, True
        if Collidable.user_input['Left']:
            dx = -1
        if Collidable.user_input['Right']:
            dx = 1
        if Collidable.user_input['Up']:
            dy = -1
        if Collidable.user_input['Down']:
            dy = 1
        self.by_direction(dx, dy)
        return ret
