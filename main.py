from utils import load_image, TILE_SIZE, SCREEN_X, SCREEN_Y, build_tile_list
from player import Player
from enemy import Enemy
from ui import UI, COLOR_2, COLOR_3
from events import event_queue
from element import Element

import pygame
import sys
import map

pygame.init()
# Device display metadata object
info = pygame.display.Info()
SCREEN_X = info.current_w
SCREEN_Y = info.current_h
clock = pygame.Clock()
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y), pygame.FULLSCREEN)
pygame.display.set_caption('Warrior Travails')
ui = UI(screen) # Instance of the UI class

# Initializing the player
player = Player(950, [500, 300])
playergroup = pygame.sprite.GroupSingle()
playergroup.add(player)

# Initializing enemies
skeleton = Enemy('skeleton_1', 90, [200, 250])
skeleton_2 = Enemy('skeleton_1', 90, [750, 250])
enemiesgroup = pygame.sprite.Group()
enemiesgroup.add([skeleton, skeleton_2])

# Horizontal movement flags
left_pressed = False
right_pressed = False

# Generating a 2d list of the map
map_list = map.generate_map()
# Tile list is a list with tile rects and types
tile_list = build_tile_list(map_list)
# Helps the UI highlight
j_key_pressed = False
k_key_pressed = False

# Flag to signal if the game started to be played
in_gameplay = False

# Flag to signal if the game should render the main menu
in_main_menu = True

title_imgdata = { 'imgname': 'header_art.png', 'subpath': ['graphics', 'ui', 'menu'] }
title_textdata =  { 'size': 20, 'content': 'Warrior Travails', 'color': COLOR_2}
title_pos = (SCREEN_X // 2, 300) 

# Creating the game title text
game_title = Element(title_imgdata, title_textdata, title_pos)
game_title.scale(double = True)

newgame_imgdata = { 'imgname': 'button_1.png', 'subpath': ['graphics', 'ui', 'menu'] }
newgame_textdata = { 'size': 14, 'content': 'New Game', 'color': COLOR_2 }
newgame_pos = (SCREEN_X // 2, 400)

newgame_button = Element(newgame_imgdata, newgame_textdata, newgame_pos)

quit_imgdata = { 'imgname': 'button_1.png', 'subpath': ['graphics', 'ui', 'menu'] }
quit_textdata = { 'size': 14, 'content': 'Quit', 'color': COLOR_2 }
quit_pos = (SCREEN_X // 2, 460)

quit_button = Element(quit_imgdata, quit_textdata, quit_pos)

# Background images
main_menu_bg = load_image('main_menu_bg.png', ['graphics', 'ui', 'menu'])
main_menu_bg = pygame.transform.scale(main_menu_bg, (SCREEN_X, SCREEN_Y)) # Resizing the background properly
gameplay_bg = load_image('bg.png', ['graphics', 'world'])

while in_main_menu:
  screen.blit(main_menu_bg, (0, 0)) # rendering the background

  # Rendering menu UI
  game_title.render(screen)
  newgame_button.render(screen)
  quit_button.render(screen)

  # Event loop area
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_q:
        pygame.quit()
        sys.exit()


  pygame.display.update()
  clock.tick(60)

while in_gameplay:
    
  # Event loop area
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

    if event.type == pygame.KEYDOWN:

      # Player jump
      if event.key == pygame.K_SPACE:
        player.attacking = False # Player stops attacking while running

        if player.air_timer < 6:
          player.jump_pressed = True
          player.vertical_velocity = -16

      # Move horizontally
      if event.key == pygame.K_a:
        left_pressed = True
        player.direction = 'left'

      if event.key == pygame.K_d:
        right_pressed = True
        player.direction = 'right'

      # Melee
      if event.key == pygame.K_k:
        k_key_pressed = True
        if player.guard_cooldown == 0:
          player.guarding = True

          # Player stops moving if guarding during running
          left_pressed = False
          right_pressed = False

      if event.key == pygame.K_j:
        j_key_pressed = True
        if player.air_timer < 6 and player.attack_cooldown == 0:
          player.attacking = True
          player.attack_cooldown = 60

      # Kill player (test)
      if event.key == pygame.K_q:
        player.dead_lock = True


    if event.type == pygame.KEYUP:

      # Player jump
      if event.key == pygame.K_SPACE:
        player.jump_pressed = False

      # Move horizontally
      if event.key == pygame.K_a:
        left_pressed = False
      if event.key == pygame.K_d:
        right_pressed = False

      # Melee
      if event.key == pygame.K_k:
        player.guarding = False
        k_key_pressed = False
      if event.key == pygame.K_j:
        j_key_pressed = False

  # Main blitting area
  screen.blit(gameplay_bg, (0, 0)) # rendering the background
  map.draw_map(map_list, screen, TILE_SIZE)

  # Enemies render and update
  enemies_list = enemiesgroup.sprites()
  for e in enemies_list:
    e.draw(screen)
  enemiesgroup.update(tile_list, player, screen)

  # Player render and update
  player.draw(screen)
  player.update(tile_list, enemies_list)

  # Draw the big player HP icon bar
  ui.player_hpbar(player)

  # Attack icon
  atk_img = load_image('sword_icon.png', ['graphics', 'ui'])
  atk_img_pos = (450, 20)
  ui.create_icon(atk_img, j_key_pressed, 'J', player.attack_cooldown, atk_img_pos)

  # Guard icon
  guard_img = load_image('shield_icon.png', ['graphics', 'ui'])
  guard_img_pos = (520, 20)
  ui.create_icon(guard_img, k_key_pressed, 'K', player.guard_cooldown, guard_img_pos)

  # Render entity health bars
  if player.hp < player.max_hp:
    ui.unit_hpbar(player, "#5deb20")
  for i in range(len(enemies_list)):
    mob = enemies_list[i]
    if mob.hp < mob.max_hp:
      ui.unit_hpbar(mob)

  # Event queue loop
  for e in event_queue:
    # Handling what combat event needs to be displayed
    event_surf, event_rect = e.ui
    e.vanish_timer -= 1
    if e.vanish_timer > 0:
      event_rect.y -= 1
      screen.blit(event_surf, event_rect)
    else:
      event_queue.remove(e)
  
  # Makes sure that suddle moving direction changes don't stop player's movement
  if left_pressed:
    player.movement[0] = -2
  elif right_pressed:
    player.movement[0] = 2
  else:
    player.movement[0] = 0

  pygame.display.update()
  clock.tick(60)