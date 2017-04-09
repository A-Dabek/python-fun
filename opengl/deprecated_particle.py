import random

from opengl import global_vars as GV
from opengl.collidables.movement import Movement
from opengl.collidables.surface import SurfaceList


class IEffects:
    @staticmethod
    def dim(effect, actor):
        actor._surface[(0, 'color')] = 'same', effect._duration / effect.duration
        return 1

    @staticmethod
    def damage(effect, actor):
        actor._health -= effect.damage
        pass

    @staticmethod
    def knockback(effect, actor):
        if not actor.collidable:
            effect._duration = -1
            return
        cx, cy = actor._movement.X, actor._movement.Y
        ax, ay = actor._movement.aX, actor._movement.aY
        col_ax, col_ay = effect.duration, effect.damage
        actor._movement.moveBack(cx - (2 * ax - col_ax), cy - (2 * ay - col_ay))
        effect._duration = -1


class Effect:
    _effects = {
        'strike': IEffects.damage,
        'dim': IEffects.dim,
        'knockback': IEffects.knockback
    }

    def __init__(self, name='strike', duration=0.0, damage=1.0):
        self.duration = duration
        self._duration = duration
        self.damage = damage
        self._damage = damage
        self._effect = Effect._effects[name]

    def affect(self, actor):
        if self._effect is None:
            return 0
        self._effect(self, actor)

        self._duration -= 1 / GV.FPS
        if self._duration <= 0:
            self._effect = None
            return 0
        return 1


class Collidable:
    _speed_limit = 10
    _AIs = ('straight', 'random', 'key_controlled')
    _collision = ('collide', 'pass', 'explode')
    _passives = ('',)
    user_input = {}

    def __init__(self, health=1., damage=1., size=1., size_per_unit=10,
                 color='black', collision_size=1.0, x=0, y=0, speed=0.5,
                 movement_ai='random', collidable=True, ability=None, passive=None):
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

        self._ability = None
        if ability == 'simple':
            self._ability = Ability(caster=self)

        if passive not in Collidable._passives:
            passive = Collidable._passives[0]
        self._passive = passive

        self._effects = []

    @property
    def alive(self):
        return self._health > 0

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
        self._effects.append(*efx)

    def collision_reacts(self):
        return [Effect(name='strike', duration=0, damage=0.01)]

    def to_position(self, x, y):
        self._movement.slideTo(x, y)

    def by_direction(self, x, y):
        self._movement.fly(x, y)

    def move(self):
        ret = None

        # actor passive effects
        e_iter = 0
        while e_iter < len(self._effects):
            if self._effects[e_iter].affect(self) == 0:
                del self._effects[e_iter]
            else:
                e_iter += 1

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
        if self._ability is None:
            return None
        x, y = self.centerpoint
        return self._ability.fire(x, y)

    def move_empty(self):
        return False

    def move_random(self):
        if not self._movement.moving:
            dX = random.randint(0, GV.SCR_W)
            dY = random.randint(0, GV.SCR_H)
            self._movement.slideTo(dX, dY)
        return False

    def move_user(self):
        dx, dy, ret = 0, 0, False
        if Collidable.user_input['Q']:
            ret = True
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


class Ability:
    _presets = ('fan', 'shot', 'simple')
    _dimming_time = 1
    _shot_type = ('simultaneous', 'continuous')

    def __init__(self, preset='simple', projectiles=1, child=None, caster=None, cooldown=4.0, lifespan=4.0, speed=0.3,
                 damage=1.0):
        if caster is None:
            raise ValueError('ability needs a caster')
        if preset not in Ability._presets:
            raise ValueError('preset not found')
        if projectiles <= 0:
            raise ValueError('ability needs at least one particle')

        self._speed = speed
        self._damage = damage
        self._lifespan = lifespan
        self._caster = caster
        self._projectiles = projectiles
        self._cooldown = cooldown
        self.__cooldown = self._cooldown
        self._effects = [Effect(name='strike', damage=1., duration=0.)]
        x, y = caster.centerpoint
        self._particles = [Collidable(health=lifespan, damage=damage, x=x, y=y, speed=speed,
                                      movement_ai='straight', collidable=True)
                           for _ in range(self._projectiles)]
        for i, p in enumerate(self._particles):
            p.by_direction(1, 0)

    def cooldown(self):
        if self.__cooldown > 0:
            self.__cooldown -= 1 / GV.FPS

    def fire(self, x, y):
        if self.__cooldown > 0:
            return None
        self.__cooldown = self._cooldown
        w, h = self._caster.shape
        particles = [Collidable(health=self._lifespan, damage=self._damage, x=x + w, y=y, speed=self._speed,
                                movement_ai='straight', collidable=False)
                     for _ in range(self._projectiles)]
        for i, p in enumerate(particles):
            p.by_direction(1, 0)
            p.add_effects(Effect(name='dim', damage=1., duration=4.))
        return particles
