from utils import load_image, TILE_SIZE, build_tile_list
from player import Player
from enemy import Enemy
import pygame
import sys
import map

SCREEN_X = 1400
SCREEN_Y = 640

pygame.init()
clock = pygame.Clock()
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y), pygame.RESIZABLE)
pygame.display.set_caption('Warrior Travails')

# Initializing the player
player = Player(400, [800, 250])
playergroup = pygame.sprite.GroupSingle()
playergroup.add(player)

# Initializing enemies
skeleton = Enemy('skeleton_1', 250, [900, 250])
enemiesgroup = pygame.sprite.Group()
enemiesgroup.add(skeleton)

# Horizontal movement flags
left_pressed = False
right_pressed = False

bg = load_image('bg.png', ['graphics', 'world'])
# Generating a 2d list of the map
map_list = map.generate_map()
# Tile list is a list with tile rects and types
tile_list = build_tile_list(map_list)

while True:
    
  # Event loop area
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

    if event.type == pygame.KEYDOWN:

      # Player jump
      if event.key == pygame.K_SPACE:
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
        player.guarding = True
      if event.key == pygame.K_j:
        player.attacking = True

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
      if event.key == pygame.K_j:
        player.attacking = False

  # Main blitting area
  screen.blit(bg, (0, 0)) # rendering the background
  map.draw_map(map_list, screen, TILE_SIZE)

  # Enemies render and update
  enemiesgroup.draw(screen)
  skeleton.update(tile_list)
  enemies_list = enemiesgroup.sprites()

  # Player render and update
  playergroup.draw(screen)
  player.update(tile_list, enemies_list)

  # pygame.draw.rect(screen, '#ff0000', player.rect, 2)
  pygame.draw.rect(screen, '#0000ff', skeleton.rect, 2)
  
  # Makes sure that suddle moving direction changes don't stop player's movement
  if left_pressed:
    player.movement[0] = -2
  elif right_pressed:
    player.movement[0] = 2
  else:
    player.movement[0] = 0

  pygame.display.update()
  clock.tick(60)

# what an attack is?
# a rect collision between the attacker and the defender