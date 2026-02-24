from utils import load_image, TILE_SIZE, SCREEN_X, SCREEN_Y, build_tile_list, load_sound
from buttons import get_menu_ui, get_options_ui
from particle import particles_queue, blood_slash
from events import event_queue, DamageEvent
from random import randint
from ui import UI, COLOR_4
from player import Player
from enemy import Enemy

import pygame
import sys
import map

pygame.mixer.pre_init(44100, -16, 2, 512) 
pygame.init()
pygame.mixer.set_num_channels(64) # Handles more sounds at once
clock = pygame.Clock()
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
pygame.display.set_caption('Warrior Travails')
ui = UI(screen) # Instance of the UI class
pygame.mouse.set_visible(False) # Hidding the original OS cursor

def quitgame():
  pygame.quit()
  sys.exit()

def handle_jump(player: Player) -> None:
  # Handle audio
  jumpsounds = player.sounds['jumpsound']
  jumpindex = randint(0, len(jumpsounds) - 1)
  jumpsounds[jumpindex].play()

  # Handle logic
  player.jump_pressed = True
  player.vertical_velocity = -16

def getmusic(musicname: str, subpath: list, vol: float) -> pygame.mixer.music:
  music = load_sound(musicname, subpath, True)
  pygame.mixer.music.set_volume(vol)
  pygame.mixer.music.play(-1)
  return music

def add_mob(name: str, quantity: int, pos: list) -> None:
  for _ in range(quantity):
    mob = Enemy(name, 90, pos)
    enemiesgroup.add(mob)

# Initializing the player
player = Player(1000, [500, 300])
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

# Flag to signal if the game state
in_gameplay = False
in_main_menu = True
in_options = False

# Audio loading
music_volume = 0.2
current_music = getmusic('menu_song.mp3', ['sound', 'ui'], music_volume)
music_drag = False # For the UI slider

# Main menu buttons
game_title, newgame_button, options_button, quit_button = get_menu_ui()

# Options buttons
back_button, game_options, frame, music_slider = get_options_ui(music_volume)

# Background images
main_menu_bg = load_image('main_menu_bg.png', ['graphics', 'ui', 'menu'])
main_menu_bg = pygame.transform.scale(main_menu_bg, (SCREEN_X, SCREEN_Y)) # Resizing the background properly
gameplay_bg = load_image('bg.png', ['graphics', 'world'])

while in_main_menu:
  screen.blit(main_menu_bg, (0, 0)) # rendering the background

  # Mouse UI logic
  mx, my = pygame.mouse.get_pos()
  click = pygame.mouse.get_pressed()
  if (click[0] or click[2]):
    curr_mouse_img = load_image('cursor_down.png', ['graphics', 'ui', 'cursor'])
    # Smaller rect so button hovering can't overlap
    mouse_click_area = pygame.Rect(mx, my, curr_mouse_img.get_width() // 4, curr_mouse_img.get_height() // 4)
  else:
    curr_mouse_img = load_image('cursor.png', ['graphics', 'ui', 'cursor'])
    # Smaller rect so button hovering can't overlap
    mouse_click_area = pygame.Rect(mx, my, curr_mouse_img.get_width() // 4, curr_mouse_img.get_height() // 4)

  # Rendering menu UI
  if in_options:
    game_options.render(screen)
    back_button.render(screen) 
    frame.render(screen)   

    # Music slider
    music_slider.render(screen)  
    music_slider.render_text((music_slider.rect.right + 30, music_slider.rect.top ), screen)
    music_slider.render_cursor(screen)

    # If the cursor hovers on the slider's cursor
    if mouse_click_area.colliderect(music_slider.cursor_rect):
      curr_mouse_img = load_image('cursor_open.png', ['graphics', 'ui', 'cursor'])

    if music_drag:
      # Dragging
      curr_mouse_img = load_image('cursor_fist.png', ['graphics', 'ui', 'cursor'])
      music_volume = music_slider.slide(mx)
      pygame.mixer.music.set_volume(music_volume)

    # Hovering logic
    back_button.hover(mouse_click_area.colliderect(back_button.rect), COLOR_4)

  else:
    game_title.render(screen)
    newgame_button.render(screen)
    options_button.render(screen)
    quit_button.render(screen)
    
    # Hovering logic  
    newgame_button.hover(mouse_click_area.colliderect(newgame_button.rect), COLOR_4)
    options_button.hover(mouse_click_area.colliderect(options_button.rect), COLOR_4)
    quit_button.hover(mouse_click_area.colliderect(quit_button.rect), COLOR_4)

  # Event loop area
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      quitgame()

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        quitgame()

    # If mouse left click is down
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

      # Back button in the options menu
      if in_options:
        if mouse_click_area.colliderect(back_button.rect):
          back_button.sound.play()
          in_options = False

        # Handling button sound here for dragging to avoid continuos sound triggering
        if mouse_click_area.colliderect(music_slider.cursor_rect):
          music_drag = True
          music_slider.sound.play()

      elif not in_options:
        # Quit button
        if mouse_click_area.colliderect(quit_button.rect):
          quit_button.sound.play()
          quitgame()

        # New game button
        elif mouse_click_area.colliderect(newgame_button.rect):
          current_music = getmusic('forest_song.mp3', ['sound', 'gameplay'], 0.4)
          in_main_menu = False
          in_gameplay = True    
          newgame_button.sound.play()

        # Options button
        elif mouse_click_area.colliderect(options_button.rect):
          in_options = True
          options_button.sound.play() 

    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
      if music_drag:
        music_drag = False
        music_slider.sound.play()

  # Rendering the custom cursor
  screen.blit(curr_mouse_img, mouse_click_area)

  pygame.display.update()
  clock.tick(60)

while in_gameplay:

  # Rendering the gameplay background
  screen.blit(gameplay_bg, (0,0)) 
  map.draw_map(map_list, screen, TILE_SIZE)

  # Event loop area
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

    # Keyboard keys instance  
    key = pygame.key.get_pressed()

    if event.type == pygame.KEYDOWN:

      # Player jump
      if event.key == pygame.K_SPACE:
        player.attacking = False # Player stops attacking while running

        if player.air_timer < 6:
          handle_jump(player)

      if event.key == pygame.K_ESCAPE:
        quitgame()

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
      if key[pygame.K_LSHIFT] and key[pygame.K_q]:
        player.dead_lock = True

      # Add mobs
      if key[pygame.K_LSHIFT] and key[pygame.K_1]:
        add_mob('skeleton_1', 1, [200, 250])

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

  # Enemies render and update
  enemies_list = enemiesgroup.sprites()
  for e in enemies_list:
    e.draw(screen)
  enemiesgroup.update(tile_list, player, screen)

  # Player render and update
  player.draw(screen)
  # Update only living enemies and ignore dead ones
  player.update(tile_list, [enemy for enemy in enemies_list if not enemy.dead_lock])

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
    # Making sure the program doesn't spawn more particles than needed
    if isinstance(e, DamageEvent) and not e.spawned_particles:
      blood_color = '#ff0000' if e.entity.name == 'Warrior' else "#c4c4c4"
      squirt_speed_factor = 3 if e.entity.dead_lock else 2
      blood_amount = 20 if e.entity.dead_lock else 10
      blood_slash(e.entity, e.hit_from, blood_amount, squirt_speed_factor, blood_color)
      e.spawned_particles = True

    # Handling what combat event needs to be displayed
    event_surf, event_rect = e.ui
    e.vanish_timer -= 1
    if e.vanish_timer > 0:
      event_rect.y -= 1
      screen.blit(event_surf, event_rect)
    else:
      event_queue.remove(e)

  # Particles queue loop
  for p in particles_queue:
    # Render the particle
    pygame.draw.rect(screen, p.color, p.rect)

    # Countdown to kill particles
    if p.vanish_timer <= 0:
      particles_queue.remove(p)
    else:
      p.vanish_timer -= 1

    # Velocity resistance
    resistance = -0.1 if p.direction == 'right' else 0.1
    # If the particle is moving
    if p.movement[0] != 0:
      if p.direction == 'right' and p.movement[0] <= 0:
        p.movement[0] = 0
      elif p.direction == 'left' and p.movement[0] >= 0:
        p.movement[0] = 0
      else:
        p.movement[0] += resistance

    # Gravity & collisions logic
    p.vertical_velocity += 0.2

    # Max value of how fast the particle can fall
    max_fall_velocity = 15

    p.vertical_velocity = min(p.vertical_velocity, max_fall_velocity)
    p.movement[1] = p.vertical_velocity
  
    # Don't count anything other than tiles to collide with
    collisions = p.move(tile_list, [])

    # If player collided with the ground, reset vertical_velocity and Y movement
    if collisions['bottom'] or collisions['top']:
      p.air_timer = 0
      p.vertical_velocity = 0
      p.movement[1] = 0
    else:
      p.air_timer += 1

  
  # Makes sure that suddle moving direction changes don't stop player's movement
  step = 0.3
  if left_pressed:
    player.movement[0] -= step
    if player.movement[0] <= -2:
      player.movement[0] = -2
  elif right_pressed:
    player.movement[0] += step
    if player.movement[0] >= 2:
      player.movement[0] = 2
  else:
    if player.movement[0] > 0:
      player.movement[0] -= step
      if player.movement[0] <= 0:
        player.movement[0] = 0

    elif player.movement[0] < 0:
      player.movement[0] += step
      if player.movement[0] >= 0:
        player.movement[0] = 0

  pygame.display.update()
  clock.tick(60)