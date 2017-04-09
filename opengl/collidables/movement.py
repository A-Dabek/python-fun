import math
from opengl import global_vars as GV


class Movement:
    def __init__(self, sx=0, sy=0, dx=0, dy=0, speed=1):
        self.dX = dx
        self.dY = dy
        self.sX = sx
        self.sY = sy
        self.X = sx
        self.Y = sy
        self.aX = 0
        self.aY = 0
        self.moving = False
        self.flying = False
        self.speed = speed

    def moveTo(self, xpos, ypos):
        self.X = xpos
        self.Y = ypos
        self.dX = xpos
        self.dY = ypos
        self.reset()
        self.moving = True

    def fly(self, ax, ay):
        self.moving = True
        self.flying = True
        summed = math.fabs(ax) + math.fabs(ay)
        if summed <= 0:
            summed = 1
        self.aX = self.speed * ax / summed
        self.aY = self.speed * ay / summed

    def moveBack(self, xpos, ypos):
        self.X = xpos
        self.Y = ypos
        self.dX = xpos
        self.dY = ypos
        self.aX = 0
        self.aY = 0
        self.moving = False

    def reset(self):
        self.sX = self.X
        self.sY = self.Y
        self.dX = self.X
        self.dY = self.Y
        self.aX = 0
        self.aY = 0
        self.moving = False

    def slideTo(self, xpos, ypos, verbose=False):
        self.dX = xpos
        self.dY = ypos
        distance = math.sqrt((self.dX - self.sX) ** 2 + (self.dY - self.sY) ** 2)
        self.aX = self.speed * (self.dX - self.sX) / distance
        self.aY = self.speed * (self.dY - self.sY) / distance
        if verbose:
            print(distance, self.sX, self.sY, self.aX, self.aY)
        self.moving = True

    def move(self):
        if not self.moving:
            return
        if self.flying:
            self.progress()
        elif self.aX * self.X >= self.aX * self.dX and self.aY * self.Y >= self.aY * self.dY:
            self.reset()
        else:
            self.progress()

    def progress(self):
        self.progress_linear()

    def progress_accelerate(self):
        self.progress_linear()
        self.aX *= 1 + self.acc / 100
        self.aY *= 1 + self.acc / 100

    def progress_linear(self):
        self.X += self.aX
        self.Y += self.aY
