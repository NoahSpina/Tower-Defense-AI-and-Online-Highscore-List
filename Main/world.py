import pygame as pg

class World():
    def __init__(self, data, map_image):
        self.waypoints = []
        self.level_data = data
        self.image = map_image
    

    #get waypoints from json
    def process_data(self):
        for layer in self.level_data["layers"]:
            if layer["name"] == "waypoints":
                for object in layer ["objects"]:
                    waypoint_data = object["polyline"]
                    self.make_waypoints(waypoint_data)
    

    def make_waypoints(self, data):
        for item in data:
            x_cord = item.get('x')         
            y_cord = item.get('y')      
            self.waypoints.append((x_cord, y_cord))


    def draw(self, surface):
        surface.blit(self.image, (0,0))