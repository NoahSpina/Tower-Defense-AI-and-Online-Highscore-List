import pygame as pg
import random
from enemy_data import ENEMY_SPAWN_DATA


class World:
    def __init__(self, data, map_image):
        self.level = 1
        self.tile_map = []
        self.waypoints = []
        self.level_data = data
        self.image = map_image
        self.enemy_list = []
        self.spawned_enemies = 0

    # get waypoints from json
    def process_data(self):
        for layer in self.level_data["layers"]:
            if layer["name"] == "tilemap":
                self.tile_map = layer["data"]
            elif layer["name"] == "waypoints":
                for obj in layer["objects"]:
                    waypoint_data = obj["polyline"]
                    self.make_waypoints(waypoint_data)

    def make_waypoints(self, data):
        for point in data:
            x_cord = point.get('x')
            y_cord = point.get('y')
            self.waypoints.append((x_cord, y_cord))

    def process_enemies(self):
        enemies = ENEMY_SPAWN_DATA[self.level - 1]
        for enemy_type in enemies:
            enemies_to_spawn = enemies[enemy_type]
            for enemy in range(enemies_to_spawn):
                self.enemy_list.append(enemy_type)
        # now randomize list to shuffle enemies
        random.shuffle(self.enemy_list)

    def draw(self, surface):
        surface.blit(self.image, (0, 0))
