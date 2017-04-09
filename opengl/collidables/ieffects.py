from .. import global_vars as GV


class IEffects:

    @staticmethod
    def dim(effect, actor):
        actor._surface[(0, 'color')] = 'same', effect._duration / effect.duration
        if effect._duration <= 0:
            actor._health = None
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
        col_ax, col_ay = effect.duration / GV.FPS, effect.damage
        actor._movement.moveBack(cx - (ax - col_ax), cy - (ay - col_ay))
        effect._duration = -1


class Effect:
    _effects = {
        'strike': IEffects.damage,
        'dim': IEffects.dim,
        'knockback': IEffects.knockback
    }

    def __init__(self, name='strike', duration=0.0, damage=1.0):
        self.duration = duration * GV.FPS
        self._duration = duration * GV.FPS
        self.damage = damage
        self._damage = damage
        self._effect = Effect._effects[name]

    def affect(self, actor):
        if self._effect is None:
            return 0
        self._duration -= 1
        self._effect(self, actor)
        if self._duration <= 0:
            self._effect = None
            return 0
        return 1
