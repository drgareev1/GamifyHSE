import pygame as pg

class Residential:

    def __init__(self, x, y, pos, type, resource_manager, app_context):
        self.app_context = app_context
        if type == "low":
            image = pg.image.load(app_context.get_resource('low.png'))
        elif type == "medium":
            image = pg.image.load(app_context.get_resource('medium.png'))
        self.image = image
        self.x = x
        self.y = y
        self.name = type
        self.rect = self.image.get_rect(topleft=pos)
        self.resource_manager = resource_manager
        self.counter = 0
        self.resource_cooldown = pg.time.get_ticks()

    def after_built(self):
        self.resource_manager.apply_cost_to_resource(self.name)
        self.resource_manager.apply_immediate_profits(self.name)

    def update(self):
        now = pg.time.get_ticks()
        if now - self.resource_cooldown > 2 * 1000:
            self.resource_manager.resources["money"] += 5
            self.resource_cooldown = now
            self.resource_manager.save_resources()


class Office:

    def __init__(self, x, y, pos, type, resource_manager, app_context):
        self.app_context = app_context
        if type == "high":
            image = pg.image.load(app_context.get_resource('high.png'))
        elif type == "skyscraper":
            image = pg.image.load(app_context.get_resource('skyscraper.png'))
        self.image = image
        self.x = x
        self.y = y
        self.name = type
        self.rect = self.image.get_rect(topleft=pos)
        self.resource_manager = resource_manager
        self.counter = 0
        self.resource_cooldown = pg.time.get_ticks()

    def update(self):
        now = pg.time.get_ticks()
        if now - self.resource_cooldown > 2 * 1000:
            self.resource_manager.resources["money"] += 8
            self.resource_cooldown = now
            self.resource_manager.save_resources()

    def after_built(self):
        self.resource_manager.apply_cost_to_resource(self.name)
        self.resource_manager.apply_immediate_profits(self.name)


class Recreational:

    def __init__(self, x, y, pos, type, resource_manager, app_context):
        self.app_context = app_context
        if type == "park":
            image = pg.image.load(app_context.get_resource('park.png'))
        elif type == "of":
            image = pg.image.load(app_context.get_resource('of.png'))
        self.image = image
        self.x = x
        self.y = y
        self.name = type
        self.rect = self.image.get_rect(topleft=pos)
        self.resource_manager = resource_manager
        self.counter = 0
        self.resource_cooldown = pg.time.get_ticks()

    def update(self):
        pass

    def after_built(self):
        self.resource_manager.apply_cost_to_resource(self.name)
        self.resource_manager.apply_immediate_profits(self.name)
