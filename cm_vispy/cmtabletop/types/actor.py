class Actor:
    def __init__(self, surface, sx=0, sy=0, dx=0, dy=0, speed=30, angle=0, start=False):
        self.surface = surface
        self.dX = dx
        self.dY = dy
        self.sX = sx
        self.sY = sy
        self.X = sx
        self.Y = sy
        self.aX = 0
        self.aY = 0
        self.moving = False
        self.tag = None
        self.speed = speed
        self.dAngle = angle
        self.sAngle = 0
        self.aAngle = 0
        if start:
            self.aX = float(self.dX - self.sX) / self.speed
            self.aY = float(self.dY - self.sY) / self.speed
            self.aAngle = self.dAngle / self.speed
            self.moving = True

    def get_coords(self):
        return self.X, self.Y

    def moveTo(self, xpos, ypos):
        self.reset()
        self.X = xpos
        self.Y = ypos
        self.dX = xpos
        self.dY = ypos
        self.moving = True

    def reset(self):
        self.sX = self.X
        self.sY = self.Y
        self.dX = self.X
        self.dY = self.Y
        self.aX = 0
        self.aY = 0
        self.moving = False

    def slideTo(self, xpos, ypos):
        self.dX = xpos
        self.dY = ypos
        self.aX = float(self.dX - self.sX) / self.speed
        self.aY = float(self.dY - self.sY) / self.speed
        self.aAngle = self.dAngle / self.speed
        self.moving = True

    def move(self):
        if not self.moving:
            return
        self.progress()
        # assert self.surface is not None
        if self.surface is not None:
            self.surface.translate(self.X, self.Y)
        if self.aX * self.X >= self.aX * self.dX and self.aY * self.Y >= self.aY * self.dY:
            self.X = self.dX
            self.Y = self.dY
            self.reset()

    def progress(self):
        self.progress_linear()

    def progress_linear(self):
        self.X += self.aX
        self.Y += self.aY
        self.sAngle += self.aAngle
