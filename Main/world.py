import pygame as pg


class World:
    def __init__(self, data, map_image):
        self.tile_map = []
        self.waypoints = []
        self.level_data = data
        self.image = map_image

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

    def draw(self, surface):
        surface.blit(self.image, (0, 0))
