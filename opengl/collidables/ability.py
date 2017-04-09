from .collidable import Collidable
from .ieffects import Effect
from .. import global_vars as GV


class Ability:
    _presets = ('fan', 'shot', 'simple')
    _dimming_time = 1
    _shot_type = ('simultaneous', 'continuous')

    def __init__(self, preset='simple', projectiles=1, child=None, caster=None, cooldown=4.0, lifespan=4.0, speed=0.3,
                 damage=1.0):
        if preset not in Ability._presets:
            raise ValueError('preset not found')
        if projectiles <= 0:
            raise ValueError('ability needs at least one particle')

        self._speed = speed
        self._damage = damage
        self._lifespan = lifespan
        self.caster = caster
        self._projectiles = projectiles
        self._cooldown = cooldown
        self.__cooldown = self._cooldown
        self._effects = [Effect(name='strike', damage=1., duration=0.)]

    def on_cooldown(self):
        return self.__cooldown > 0

    def cooldown(self):
        if self.__cooldown > 0:
            self.__cooldown -= 1 / GV.FPS

    def fire(self, dx, dy):
        if self.__cooldown > 0:
            return None
        self.__cooldown = self._cooldown
        x, y = self.caster.centerpoint
        w, h = self.caster.shape
        w *= dx
        h *= dy
        particles = [Collidable(health=self._lifespan, damage=self._damage, x=x + w, y=y + h, speed=self._speed,
                                movement_ai='straight', collidable=False)
                     for _ in range(self._projectiles)]
        for i, p in enumerate(particles):
            p.by_direction(dx, dy)
            p.add_effects(Effect(name='dim', damage=5., duration=4.))
        return particles
