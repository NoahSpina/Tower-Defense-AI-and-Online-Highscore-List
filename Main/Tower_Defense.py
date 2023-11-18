import pygame as pg
import constants as c
from enemy import Enemy
from button import Button
import os
from turret import Turret
from world import World
import json

# get working directory 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# initialize pygame
pg.init()

# create clock
clock = pg.time.Clock()

# create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defense")

# game variables
selected_turret = None
placing_turrets = False

# load images
# map
map_image = pg.image.load("levels/map.png").convert_alpha()
# turret sprite sheets
turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'Assets/Images/Turret/turret_{x}.png')
    turret_spritesheets.append(turret_sheet)
# individual turret image for mouse cursor
cursor_turret = pg.image.load('Assets/Images/Turret/cursor_turret.png').convert_alpha()
# enemies
enemy_image = pg.image.load('Assets/Images/Enemy/enemy_1.png').convert_alpha()
# buttons
buy_turret_image = pg.image.load('assets/images/button/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/images/button/cancel.png').convert_alpha()
upgrade_turret_image = pg.image.load('assets/images/button/upgrade_turret.png').convert_alpha()

# load level json
with open('levels/map.tmj') as file:
    world_data = json.load(file)


def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    # calculate the sequential number of the tile
    mouse_tile_num = mouse_tile_y * c.COLS + mouse_tile_x
    # check if that tile is grass
    if world.tile_map[mouse_tile_num] == 7:
        # check that there isn't already a turret there
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        if space_is_free:
            new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y)
            turret_group.add(new_turret)


def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret


def clear_selection():
    for turret in turret_group:
        turret.selected = False

# create world
world = World(world_data, map_image)
world.process_data()

# create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

enemy = Enemy(world.waypoints, enemy_image)
enemy_group.add(enemy)

# create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_turret_image, True)

# game loop
run = True
while run:
    clock.tick(c.FPS)
    ####
    # UPDATING
    ####

    # update groups
    enemy_group.update()
    turret_group.update(enemy_group)

    # highlight selected turret
    if selected_turret:
        selected_turret.selected = True
    
    ####
    # DRAWING
    ####
    screen.fill("grey100")
    world.draw(screen)

    # draw groups
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    # draw buttons

    if turret_button.draw(screen):
        placing_turrets = True

    # if placing turrets, show cancel button as well
    if placing_turrets:
        # show cursor turret
        cursor_rect = cursor_turret.get_rect()
        cursor_pos = pg.mouse.get_pos()
        cursor_rect.center = cursor_pos
        if cursor_pos[0] <= c.SCREEN_WIDTH:
            screen.blit(cursor_turret, cursor_rect)
        if cancel_button.draw(screen):
            placing_turrets = False

    # if a turret is selected then show the upgrade button
    if selected_turret:
        # if a turret can be upgraded, then show the upgrade button
        if selected_turret.upgrade_level < c.TURRET_LEVELS:
            if upgrade_button.draw(screen):
                selected_turret.upgrade()


    # event handler
    for event in pg.event.get():
        # quit program
        if event.type == pg.QUIT:
            run = False
        # mouse click
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            # check if mouse is on game area
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                # clear selected turrets
                selected_turret = None
                clear_selection()
                if placing_turrets:
                    create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)

    # update display
    pg.display.flip()

pg.quit()
