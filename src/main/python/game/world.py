import pygame as pg
import random
import json
from .settings import TILE_SIZE
from .buildings import Residential, Office, Recreational


class World:

    def __init__(self, username, resource_manager, entities, file_name, hud, grid_length_x, grid_length_y, width, height, app_context):

        self.app_context = app_context
        self.username = username
        self.entities = entities
        self.resource_manager = resource_manager

        self.hud = hud
        self.grid_length_x = grid_length_x
        self.grid_length_y = grid_length_y
        self.width = width
        self.height = height

        self.buildings = [[None for x in range(self.grid_length_x)] for y in range(self.grid_length_y)]

        self.grass_tiles = pg.Surface((
            grid_length_x * TILE_SIZE * 2,
            grid_length_y * TILE_SIZE + 2 * TILE_SIZE)).convert_alpha()
        self.grass_tiles.fill((29, 162, 216))
        self.tiles = self.load_images()

        try:
            with open(self.resource_manager.file_path) as f:
                data = json.load(f)
                if "buildings" in data:
                    self.world = self.load_world(data)
                else:
                    self.world = self.create_world()
                    self.save_world(file_name)
                f.close()
        except IOError:
            self.world = self.create_world()
            self.save_world(file_name)

        self.temp_tile = None
        self.examine_tile = None


    def update(self, camera):

        keys = pg.key.get_pressed()
        if keys[pg.K_BACKSPACE]:
            if self.examine_tile is not None:
                self.buildings[self.examine_tile[0]][self.examine_tile[1]] = None
                for ent in self.entities:
                    if (ent.x == self.examine_tile[0]) and (ent.y == self.examine_tile[1]):
                        self.entities.remove(ent)
                self.world[self.examine_tile[0]][self.examine_tile[1]]["tile"] = ""
                self.world[self.examine_tile[0]][self.examine_tile[1]]["collision"] = False
                self.save_world(self.username)
                self.examine_tile = None
            # delete

        mouse_pos = pg.mouse.get_pos()
        mouse_action = pg.mouse.get_pressed()

        if mouse_action[2]:
            self.examine_tile = None
            self.hud.examined_tile = None

        self.temp_tile = None
        if self.hud.selected_tile is not None:
            grid_pos = self.mouse_to_grid(mouse_pos[0], mouse_pos[1], camera.scroll)

            if self.can_place_tile(grid_pos):
                img = self.hud.selected_tile["image"].copy()
                img.set_alpha(100)

                render_pos = self.world[grid_pos[0]][grid_pos[1]]["render_pos"]
                iso_poly = self.world[grid_pos[0]][grid_pos[1]]["iso_poly"]
                collision = self.world[grid_pos[0]][grid_pos[1]]["collision"]
                connection = True
                if self.hud.selected_tile["name"] != "tree":
                    if not self.is_connected_to_road(grid_pos):
                        connection = False

                self.temp_tile = {
                    "image": img,
                    "render_pos": render_pos,
                    "collision": collision,
                    "iso_poly": iso_poly,
                    "connection": connection
                }
                will_build = False
                if mouse_action[0] and not collision:
                    if self.hud.selected_tile["name"] != "tree":
                        if self.is_connected_to_road(grid_pos):
                            will_build = True
                    else:
                        will_build = True

                    if will_build is True:

                        if (self.hud.selected_tile["name"] == "low") or (self.hud.selected_tile["name"] == "medium"):
                            ent = Residential(grid_pos[0], grid_pos[1], render_pos, self.hud.selected_tile["name"], self.resource_manager, self.app_context)
                            ent.after_built()
                            self.entities.append(ent)
                            self.buildings[grid_pos[0]][grid_pos[1]] = ent
                        elif (self.hud.selected_tile["name"] == "high") or (self.hud.selected_tile["name"] == "skyscraper"):
                            ent = Office(grid_pos[0], grid_pos[1], render_pos, self.hud.selected_tile["name"], self.resource_manager, self.app_context)
                            ent.after_built()
                            self.entities.append(ent)
                            self.buildings[grid_pos[0]][grid_pos[1]] = ent
                        elif (self.hud.selected_tile["name"] == "park") or (self.hud.selected_tile["name"] == "of"):
                            ent = Recreational(grid_pos[0], grid_pos[1], render_pos, self.hud.selected_tile["name"], self.resource_manager, self.app_context)
                            ent.after_built()
                            self.entities.append(ent)
                            self.buildings[grid_pos[0]][grid_pos[1]] = ent
                        elif (self.hud.selected_tile["name"] == "road"):
                            self.resource_manager.apply_cost_to_resource("road")

                        self.world[grid_pos[0]][grid_pos[1]]["tile"] = self.hud.selected_tile["name"]
                        self.world[grid_pos[0]][grid_pos[1]]["collision"] = True
                        self.save_world(self.username)
                        self.hud.selected_tile = None

        else:
            grid_pos = self.mouse_to_grid(mouse_pos[0], mouse_pos[1], camera.scroll)
            if self.can_place_tile(grid_pos):
                building = self.buildings[grid_pos[0]][grid_pos[1]]
                collision = self.world[grid_pos[0]][grid_pos[1]]["collision"]

                if mouse_action[0] and collision:
                    self.examine_tile = grid_pos
                    # self.hud.examined_tile = building

    def draw(self, screen, camera):

        screen.blit(self.grass_tiles, (camera.scroll.x, camera.scroll.y))

        for x in range(self.grid_length_x):
            for y in range(self.grid_length_y):
                render_pos = self.world[x][y]["render_pos"]

                #draw tiles

                tile = self.world[x][y]["tile"]
                if tile != "":
                    screen.blit(self.tiles[tile],
                                     (render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                                      render_pos[1] - (self.tiles[tile].get_height() - TILE_SIZE) + camera.scroll.y))

                 #draw buildings
                building = self.buildings[x][y]
                if building is not None:
                    screen.blit(building.image,
                                     (render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                                      render_pos[1] - (building.image.get_height() - TILE_SIZE) + camera.scroll.y))

                    pass

                if self.examine_tile is not None:
                    if (x == self.examine_tile[0]) and (y == self.examine_tile[1]):
                        mask = pg.mask.from_surface(self.tiles[tile]).outline()
                        mask = [(x + render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x, y + render_pos[1] - (self.tiles[tile].get_height() - TILE_SIZE) + camera.scroll.y) for x, y in mask]
                        pg.draw.polygon(screen, (255, 255, 255), mask, 3)


        if self.temp_tile is not None:
            iso_poly = self.temp_tile["iso_poly"]
            iso_poly = [(x + self.grass_tiles.get_width() / 2 + camera.scroll.x, y + camera.scroll.y) for x, y in iso_poly]
            if (self.temp_tile["collision"]):
                pg.draw.polygon(screen, (255, 0, 0), iso_poly, 3)
            elif (not self.temp_tile["connection"]):
                pg.draw.polygon(screen, (255, 135, 0), iso_poly, 3)
            else:
                pg.draw.polygon(screen, (255, 255, 255), iso_poly, 3)
            render_pos = self.temp_tile["render_pos"]
            screen.blit(
                self.temp_tile["image"],
                (
                    render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                    render_pos[1] - (self.temp_tile["image"].get_height() - TILE_SIZE) + camera.scroll.y
                )
            )

    def create_world(self):

        world = []

        for grid_x in range(self.grid_length_x):
            world.append([])
            for grid_y in range(self.grid_length_y):

                tile = ""

                if (grid_x == 15) and (self.grid_length_y - grid_y <= 3):
                    tile = "road"
                else:
                    rand_number = random.randint(0, 100)
                    if rand_number <= 5:
                        tile = "tree"

                world_tile = self.grid_to_world(tile, grid_x, grid_y)
                world[grid_x].append(world_tile)

                render_pos = world_tile["render_pos"]
                self.grass_tiles.blit(self.tiles["block"], (render_pos[0] + self.grass_tiles.get_width() / 2, render_pos[1]))

        return world

    def load_world(self, data):

        world = []
        for grid_x in range(self.grid_length_x):
            world.append([])
            for grid_y in range(self.grid_length_y):

                tile = ""

                for building in data["buildings"]:

                    if (building['x'] == grid_x) and (building['y'] == grid_y):

                        tile = building["tile"]

                world_tile = self.grid_to_world(tile, grid_x, grid_y)
                render_pos = world_tile["render_pos"]

                if (tile == "low") or (tile == "medium"):
                    ent = Residential(grid_x, grid_y, render_pos, tile, self.resource_manager, self.app_context)
                    self.entities.append(ent)
                    self.buildings[grid_x][grid_y] = ent
                elif (tile == "high") or (tile == "skyscraper"):
                    ent = Office(grid_x, grid_y, render_pos, tile, self.resource_manager, self.app_context)
                    self.entities.append(ent)
                    self.buildings[grid_x][grid_y] = ent
                elif (tile == "park") or (tile == "of"):
                    ent = Recreational(grid_x, grid_y, render_pos, tile, self.resource_manager, self.app_context)
                    self.entities.append(ent)
                    self.buildings[grid_x][grid_y] = ent

                world[grid_x].append(world_tile)
                self.grass_tiles.blit(self.tiles["block"], (render_pos[0] + self.grass_tiles.get_width() / 2, render_pos[1]))

        return world

    def save_world(self, file_name):
        world_data = {"buildings": []}
        for grid_x in range(self.grid_length_x):
            for grid_y in range(self.grid_length_y):
                if self.world[grid_x][grid_y]["tile"] != "":
                    tile_data = {'x': self.world[grid_x][grid_y]["grid"][0],
                                 'y': self.world[grid_x][grid_y]["grid"][1],
                                 'tile': self.world[grid_x][grid_y]["tile"]}
                    world_data["buildings"].append(tile_data)

        total_data = {}
        try:
            with open(self.resource_manager.file_path) as f:
                total_data = json.load(f)
                total_data["buildings"] = world_data["buildings"]
                f.close()
        except IOError:
            total_data["buildings"] = world_data["buildings"]

        with open(self.resource_manager.file_path, 'w+') as f:
            f.seek(0)
            json.dump(total_data, f, indent=4)
            f.truncate()
        f.close()

    def grid_to_world(self, tile, grid_x, grid_y):

        rect = [
            (grid_x * TILE_SIZE, grid_y * TILE_SIZE),
            (grid_x * TILE_SIZE + TILE_SIZE, grid_y * TILE_SIZE),
            (grid_x * TILE_SIZE + TILE_SIZE, grid_y * TILE_SIZE + TILE_SIZE),
            (grid_x * TILE_SIZE, grid_y * TILE_SIZE + TILE_SIZE)
        ]

        iso_poly = [self.cart_to_iso(x, y) for x, y in rect]

        minx = min([x for x, y in iso_poly])
        miny = min([y for x, y in iso_poly])

        if tile == "":
            collision = False
        else:
            collision = True

        out = {
            "grid": [grid_x, grid_y],
            "cart_rect": rect,
            "iso_poly": iso_poly,
            "render_pos": [minx, miny],
            "tile": tile,
            "collision": collision
        }

        return out

    def cart_to_iso(self, x, y):
        iso_x = x - y
        iso_y = (x + y) / 2
        return iso_x, iso_y

    def mouse_to_grid(self, x, y, scroll):
        world_x = x - scroll.x - self.grass_tiles.get_width()/2
        world_y = y - scroll.y

        cart_y = (2 * world_y - world_x) / 2
        cart_x = cart_y + world_x

        grid_x = int(cart_x) // TILE_SIZE
        grid_y = int(cart_y) // TILE_SIZE

        return grid_x, grid_y

    def load_images(self):
        block = pg.image.load(self.app_context.get_resource('block.png')).convert_alpha()
        tree = pg.image.load(self.app_context.get_resource('tree.png')).convert_alpha()
        road = pg.image.load(self.app_context.get_resource('road.png')).convert_alpha()
        skyscraper = pg.image.load(self.app_context.get_resource('skyscraper.png')).convert_alpha()
        high = pg.image.load(self.app_context.get_resource('high.png')).convert_alpha()
        medium = pg.image.load(self.app_context.get_resource('medium.png')).convert_alpha()
        low = pg.image.load(self.app_context.get_resource('low.png')).convert_alpha()
        of = pg.image.load(self.app_context.get_resource('of.png')).convert_alpha()
        park = pg.image.load(self.app_context.get_resource('park.png')).convert_alpha()

        return {"block": block,
                "tree": tree,
                "road": road,
                "skyscraper": skyscraper,
                "high": high,
                "medium": medium,
                "low": low,
                "of": of,
                "park": park
                }

    def is_connected_to_road(self, grid_pos):
        is_connected = False

        if ((self.world[grid_pos[0] - 1][grid_pos[1]]["tile"] == "road") or
            (self.world[grid_pos[0] + 1][grid_pos[1]]["tile"] == "road") or
            (self.world[grid_pos[0]][grid_pos[1] - 1]["tile"] == "road") or
            (self.world[grid_pos[0]][grid_pos[1] + 1]["tile"] == "road")):
            is_connected = True

        return is_connected

    def can_place_tile(self, grid_pos):

        world_bounds = (0 < grid_pos[0] < self.grid_length_x - 1) and (0 < grid_pos[1] < self.grid_length_y - 1)
        if not world_bounds:
            return False
        else:
            mouse_on_panel = False
            for rect in [self.hud.resources_rect, self.hud.build_rect, self.hud.select_rect]:
                if rect.collidepoint(pg.mouse.get_pos()):
                    mouse_on_panel = True

            if not mouse_on_panel:
                return True
            else:
                return False
