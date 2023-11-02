import pygame as pg
import constants as c
from enemy import Enemy
import os
from world import World
import json

# get working directory 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#initialize pygame
pg.init()

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defense")

#load images
map_image = pg.image.load("levels/map.png").convert_alpha()
enemy_image = pg.image.load('Assets/Images/Enemy/enemy_1.png').convert_alpha()

#load level json
with open('levels/map.tmj') as file:
    world_data = json.load(file)

#create world
world = World(world_data, map_image)
world.process_data()

#create groups
enemy_group = pg.sprite.Group()


enemy = Enemy(world.waypoints, enemy_image)
enemy_group.add(enemy)

#game loop
run = True
while run:
    clock.tick(c.FPS)

    screen.fill("grey100")
    world.draw(screen)

    #draw enemy path
    pg.draw.lines(screen, "grey0", False, world.waypoints)

    #update groups
    enemy_group.update()

    #draw groups
    enemy_group.draw(screen)

    #event handler
    for event in pg.event.get():
        #quit program
        if event.type == pg.QUIT:
            run = False

    #update display
    pg.display.flip()

pg.quit()
