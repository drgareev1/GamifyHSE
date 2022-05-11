from fbs_runtime.application_context.PySide2 import ApplicationContext

import pygame as pg

from .camera import Camera
from .world import World
from .settings import WINDOW_WIDTH, WINDOW_HEIGHT
from .hud import HUD
from .resource_manager import ResourceManager


class Game:

    def __init__(self, screen, clock, username, resource_manager, app_context):
        self.app_context = app_context
        self.entities = []
        self.username = username
        self.resource_manager = resource_manager
        self.screen = screen
        self.clock = clock
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.hud = HUD(self.resource_manager, self.width, self.height, self.app_context)
        self.world = World(username, self.resource_manager, self.entities, self.username, self.hud, 31, 31, self.width, self.height, self.app_context)
        self.camera = Camera(self.width, self.height)
        pg.display.set_caption('SmartLMS | Игровой мир')
        
        programIcon = pg.image.load(app_context.get_resource('icon.png'))
        pg.display.set_icon(programIcon)


    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(60)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

    def update(self):
        self.camera.update()
        self.hud.update()
        self.world.update(self.camera)
        for e in self.entities:
            e.update()

    def draw(self):
        self.screen.fill((29, 162, 216))
        self.world.draw(self.screen, self.camera)
        self.hud.draw(self.screen)
        pg.display.flip()
