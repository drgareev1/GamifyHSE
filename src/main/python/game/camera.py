import pygame as pg


class Camera:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.scroll = pg.Vector2(0, 0)
        self.dx = 0
        self.dy = 0
        self.speed = 25

    def update(self):

        keys = pg.key.get_pressed()

        if keys[pg.K_RIGHT]:
            self.dx = -self.speed
        elif keys[pg.K_LEFT]:
            self.dx = self.speed
        else:
            self.dx = 0

        if keys[pg.K_DOWN]:
            self.dy = -self.speed
        elif keys[pg.K_UP]:
            self.dy = self.speed
        else:
            self.dy = 0

        self.scroll.x += self.dx
        self.scroll.y += self.dy
