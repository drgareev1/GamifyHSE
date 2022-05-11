import pygame as pg

class HUD:

    def __init__(self, resource_manager, width, height, app_context):

        self.app_context = app_context
        self.resource_manager = resource_manager
        self.width = width
        self.height = height

        self.hud_color = (235, 235, 235, 245)

        # resources hud
        self.resources_surface = pg.Surface((width, height * 0.04), pg.SRCALPHA)
        self.resources_rect = self.resources_surface.get_rect(topleft=(0, 0))
        self.resources_surface.fill(self.hud_color)

        # building hud
        self.build_surface = pg.Surface((width * 0.05, height * 0.5), pg.SRCALPHA)
        self.build_rect = self.build_surface.get_rect(topleft=(self.width * 0.02, self.height * 0.06))
        self.build_surface.fill(self.hud_color)

        # select hud
        self.select_surface = pg.Surface((width * 0.3, height * 0.08), pg.SRCALPHA)
        self.select_rect = self.select_surface.get_rect(topleft=(self.width * 0.09, self.height * 0.06))
        self.select_surface.fill(self.hud_color)

        self.images = self.load_images()
        self.tiles = self.create_build_hud()

        self.selected_tile = None
        self.examined_tile = None
        self.hovering_tile = None

    def create_build_hud(self):

        render_pos = [self.width * 0.02 + 25, self.height * 0.06 + 10]
        object_width = self.build_surface.get_width() // 3

        tiles = []

        for image_name, image in self.images.items():

            pos = render_pos.copy()
            image_tmp = image.copy()
            image_scale = self.scale_image(image_tmp, w=object_width)
            rect = image_scale.get_rect(topleft=pos)

            tiles.append(
                {
                    "name": image_name,
                    "icon": image_scale,
                    "image": self.images[image_name],
                    "rect": rect,
                    "affordable": True
                }
            )

            render_pos[1] += image_scale.get_height() + 20

        return tiles

    def update(self):

        mouse_pos = pg.mouse.get_pos()
        mouse_action = pg.mouse.get_pressed()

        if mouse_action[2]:
            self.selected_tile = None

        self.hovering_tile = None

        for tile in self.tiles:
            if self.resource_manager.can_build(tile["name"]):
                tile["affordable"] = True
            else:
                tile["affordable"] = False
            if tile["rect"].collidepoint(mouse_pos):
                self.hovering_tile = tile
                if mouse_action[0] and (tile["affordable"]):
                    self.selected_tile = tile

    def draw(self, screen):

        # resources hud
        screen.blit(self.resources_surface, (0, 0))
        # build hud
        screen.blit(self.build_surface, (self.width * 0.02, self.height * 0.06))
        # select hud
        if self.hovering_tile is not None:
            w, h = self.select_rect.width, self.select_rect.height
            screen.blit(self.select_surface, (self.width * 0.08, self.height * 0.06))
            img = self.images[self.hovering_tile["name"]].copy()
            img_scale = self.scale_image(img, h=h*0.7)
            screen.blit(img_scale, (self.width * 0.08 + 16, self.height * 0.072))

            resources_text = ""
            costs = self.resource_manager.costs[self.hovering_tile["name"]]
            for key, value in costs.items():
                resources_text = resources_text + str(key) + ': ' + str(value) + ", "
            self.draw_text(screen, resources_text[:-2], 40, (0,0,0), (self.select_rect.center[0] - 142, self.select_rect.center[1] - 16))

        if self.examined_tile is not None:
            print(self.examined_tile.counter)

        for tile in self.tiles:
            icon = tile["icon"].copy()
            if not tile["affordable"]:
                icon.set_alpha(100)
            screen.blit(icon, tile["rect"].topleft)

        pos = 8
        for resource, resource_value in self.resource_manager.resources.items():
            text = self.resource_manager.resource_names[resource] + ": " + str(resource_value)
            self.draw_text(screen, text, 36, (0, 0, 0), (pos, 6))
            pos += 250

    def load_images(self):
        tree = pg.image.load(self.app_context.get_resource('tree.png')).convert_alpha()
        road = pg.image.load(self.app_context.get_resource('road.png')).convert_alpha()
        skyscraper = pg.image.load(self.app_context.get_resource('skyscraper.png')).convert_alpha()
        high = pg.image.load(self.app_context.get_resource('high.png')).convert_alpha()
        medium = pg.image.load(self.app_context.get_resource('medium.png')).convert_alpha()
        low = pg.image.load(self.app_context.get_resource('low.png')).convert_alpha()
        of = pg.image.load(self.app_context.get_resource('of.png')).convert_alpha()
        park = pg.image.load(self.app_context.get_resource('park.png')).convert_alpha()

        return {"road": road,
                "tree": tree,
                "low": low,
                "medium": medium,
                "high": high,
                "skyscraper": skyscraper,
                "of": of,
                "park": park
                }

    def scale_image(self, image, w=None, h=None):

        if (w is None) and (h is None):
            pass
        elif h is None:
            scale = w / image.get_width()
            h = scale * image.get_height()
            image = pg.transform.scale(image, (int(w), int(h)))
        elif w is None:
            scale = h / image.get_height()
            w = scale * image.get_width()
            image = pg.transform.scale(image, (int(w), int(h)))
        else:
            image = pg.transform.scale(image, (int(w), int(h)))

        return image

    def draw_text(self, screen, text, size, colour, pos):

        font = pg.font.Font(self.app_context.get_resource('HSESans-Regular.otf'), 24)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect(topleft=pos)

        screen.blit(text_surface, text_rect)
