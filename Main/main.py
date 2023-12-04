import pygame as pg
import pygame_gui
import sys
import constants as c
from enemy import Enemy
from button import Button
import os
from turret import Turret
from world import World
import json
from firebase_admin import db
from config import firebaseConfig
import pyrebase
from datetime import datetime

# get working directory 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# initialize pygame
pg.init()

# create clock and window
clock = pg.time.Clock()
MANAGER = pygame_gui.UIManager((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
end_game_info = {}
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defense")

#link to firebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# game variables
game_over = False
# -1 = lose & 1 is a win
game_outcome = 0
last_enemy_spawn = pg.time.get_ticks()
selected_turret = None
placing_turrets = False
level_started = False

# load images
# map
map_image = pg.image.load("levels/map.png").convert_alpha()
# load turret sprite sheets
turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'Assets/Images/Turret/turret_{x}.png')
    turret_spritesheets.append(turret_sheet)
# individual turret image for mouse cursor
cursor_turret = pg.image.load('Assets/Images/Turret/cursor_turret.png').convert_alpha()
# enemies
enemy_images = {
    "weak": pg.image.load('Assets/Images/Enemy/enemy_1.png').convert_alpha(),
    "medium": pg.image.load('Assets/Images/Enemy/enemy_2.png').convert_alpha(),
    "strong": pg.image.load('Assets/Images/Enemy/enemy_3.png').convert_alpha(),
    "elite": pg.image.load('Assets/Images/Enemy/enemy_4.png').convert_alpha()
}
# buttons
buy_turret_image = pg.image.load('assets/images/button/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/images/button/cancel.png').convert_alpha()
upgrade_turret_image = pg.image.load('assets/images/button/upgrade_turret.png').convert_alpha()
begin_image = pg.image.load('assets/images/button/begin.png').convert_alpha()
restart_image = pg.image.load('assets/images/button/restart.png').convert_alpha()
fast_forward_image = pg.image.load('assets/images/button/fast_forward.png').convert_alpha()

# gui
heart_image = pg.image.load('assets/images/gui/heart.png').convert_alpha()
logo_image = pg.image.load('assets/images/gui/logo.png').convert_alpha()
coin_image = pg.image.load('assets/images/gui/coin.png').convert_alpha()

shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(0.5)

# load json data for for level creation
with open('levels/map.tmj') as file:
    world_data = json.load(file)

# load fonts for displaying text on the screen
text_font = pg.font.SysFont("Consolas", 24, bold=True)
large_font = pg.font.SysFont("Consolas", 36)
small_font = pg.font.SysFont("Consolas", 20)


# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def display_data():
    # draw panel
    pg.draw.rect(screen, "maroon", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
    pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
    screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
    # display data
    draw_text("LEVEL " + str(world.level), text_font, "grey100", c.SCREEN_WIDTH + 10, 10)
    draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH + 50, 40)
    screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
    draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH + 50, 70)
    screen.blit(coin_image, (c.SCREEN_WIDTH + 10, 65))


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
            new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
            turret_group.add(new_turret)
            # deduct cost of turret
            world.money -= c.BUY_COST


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
world.process_enemies()

# create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

# create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 300, begin_image, True)
restart_button = Button(310, 400, restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH + 50, 300, fast_forward_image, False)

# game loop
run = True
while run:
    clock.tick(c.FPS)
    UI_REFRESH_RATE = clock.tick(60)/1000
    #####################
    # UPDATING
    #####################

    if not game_over:
        if world.health <= 0:
            game_over = True
            # loss
            NAME_INPUT = pygame_gui.elements.UITextEntryLine(relative_rect=pg.Rect((325,330), (150, 40)), manager=MANAGER, 
                                                                                   object_id = "#name_entry")
            game_outcome = -1
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            # win
            NAME_INPUT = pygame_gui.elements.UITextEntryLine(relative_rect=pg.Rect((325,330), (150, 40)), manager=MANAGER, 
                                                                                   object_id = "#name_entry")
            game_outcome = 1

        # update groups
        enemy_group.update(world)
        turret_group.update(enemy_group, world)

        # highlight selected turret
        if selected_turret:
            selected_turret.selected = True
    
    #####################
    # DRAWING
    #####################

    # draw level
    world.draw(screen)

    # draw groups
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    display_data()

    if not game_over:
        # check if the level has been started or not
        if not level_started:
            if begin_button.draw(screen):
                level_started = True
        else:
            # fast-forward option
            world.game_speed = 1
            if fast_forward_button.draw(screen):
                world.game_speed = 2
            # spawn enemies
            if pg.time.get_ticks() - last_enemy_spawn > (c.SPAWN_COOLDOWN / world.game_speed):
                if world.spawned_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                    enemy_group.add(enemy)
                    world.spawned_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()

        # check if the wave is finished
        if world.check_level_complete():
            world.money += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = False
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()

        # draw buttons
        # Here is the button for placing turrets
        # for the turret button, show cost of turret and draw the button
        draw_text(str(c.BUY_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 135)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
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
                # show cost of upgrade
                draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
                screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
                if upgrade_button.draw(screen):
                    if world.money >= c.UPGRADE_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST
    else:
        pg.draw.rect(screen, "dodgerblue", (150, 200, 500, 350), border_radius=30)
        draw_text("Type name, press enter, and", small_font, "grey0", 245, 270)
        draw_text("hit restart to upload results!", small_font, "grey0", 235, 300)
        if game_outcome == -1:
            draw_text("GAME OVER", large_font, "grey0", 310, 230)
        elif game_outcome == 1:
            draw_text("YOU WIN!", large_font, "grey0", 315, 230)
        # restart button
        if restart_button.draw(screen):
            if 'user' in end_game_info:
                #create upload object
                end_game_info['level'] = world.level
                end_game_info['remaining_health'] = world.health
                end_game_info['money'] = world.money
                now = datetime.now()
                formatted_datetime = now.strftime("%Y-%m-%d %H:%M")
                end_game_info['time'] = formatted_datetime
                upload_object = end_game_info
                #push to firebase
                db.child("/FinalScores").push(upload_object)
                print(upload_object)
            #kill name input if it still exists (name hasnt been inputed)
            if NAME_INPUT:
                NAME_INPUT.kill()
            
            game_over = False
            level_started = False
            placing_turrets = False
            selected_turret = None
            last_enemy_spawn = pg.time.get_ticks()
            world = World(world_data, map_image)
            world.process_data()
            world.process_enemies()
            # empty groups
            enemy_group.empty()
            turret_group.empty()
            #reset end game info
            end_game_info = {}

    # event handler
    for event in pg.event.get():
        # quit program
        if event.type == pg.QUIT:
            run = False
        # mouse click
        MANAGER.process_events(event)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            # check if mouse is on game area
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                # clear selected turrets
                selected_turret = None
                clear_selection()
                if placing_turrets:
                    # check if there is enough money for a turret
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_object_id == "#name_entry":
            end_game_info['user'] = event.text
            NAME_INPUT.kill()
    MANAGER.update(UI_REFRESH_RATE)
    MANAGER.draw_ui(screen)

    # update display
    pg.display.flip()

pg.quit()
