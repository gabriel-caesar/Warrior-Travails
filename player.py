from utils import load_sprite_imgs
from entity import Entity
import pygame
import map

# Animation imports
player_imgs = load_sprite_imgs(['player'])
(
  attack_1, attack_2, guard_1, 
  idle_1, jump_1, walk_1, 
  walk_2, walk_3, walk_4
) = player_imgs.values()

class Player(pygame.sprite.Sprite, Entity):
  def __init__(self, hp, pos):
    pygame.sprite.Sprite.__init__(self)
    Entity.__init__(self, hp, pos)

    self.animation_state = 'idle'
    self.animation_index = 0
    self.player_frames = []
    self.image = idle_1
    self.rect = self.image.get_rect(midbottom = (pos[0], pos[1]))
    self.mask = pygame.mask.from_surface(self.image)
    self.jump_pressed = False
  
  def animate(self):
    # Handling flipping logic
    if self.direction == 'right':
      self.flip = False
    elif self.direction == 'left':
      self.flip = True

    match self.animation_state:

      case 'run':
        self.player_frames = [ walk_1, walk_2, walk_3, walk_4 ]
        self.animation_index += 0.1

        if (self.animation_index > len(self.player_frames)):
          self.animation_index = 0

        self.image = pygame.transform.flip(self.player_frames[int(self.animation_index)], self.flip, False)

      case 'attack':
        self.player_frames = [ attack_2 ]

        self.animation_index += 0.1

        if (self.animation_index > len(self.player_frames)):
          self.animation_index = 0
        
        self.image = pygame.transform.flip(self.player_frames[int(self.animation_index)], self.flip, False)

      case 'guard':
        self.player_frames = [ guard_1 ]
        self.image = pygame.transform.flip(self.player_frames[0], self.flip, False)

      case 'jump':
        self.player_frames = [ jump_1 ]
        self.image = pygame.transform.flip(self.player_frames[0], self.flip, False)

      case 'idle':
        self.player_frames = [ idle_1 ]
        self.image = pygame.transform.flip(self.player_frames[0], self.flip, False)
        self.rect = self.image.get_rect()

  def update(self, tile_list, enemies_list):
    # Handling animation state
    if self.air_timer > 3:
      self.animation_state = 'jump'
    elif self.movement[0] != 0:
      self.animation_state = 'run'
    elif self.attacking:
      self.animation_state = 'attack'
    elif self.guarding:
      self.animation_state = 'guard'
    else:
      self.animation_state = 'idle'
    
    self.animate()

    self.attack(enemies_list)

    # Gravity & collisions logic
    self.vertical_velocity += 1

    # If the space bar is held, the player falls slower 
    max_fall_velocity = 4 if self.jump_pressed else 15

    self.vertical_velocity = min(self.vertical_velocity, max_fall_velocity)
    self.movement[1] = self.vertical_velocity - 0.5
  
    collisions = self.move(tile_list, enemies_list)

    # If player collided with the ground, reset vertical_velocity and Y movement
    if collisions['bottom'] or collisions['top']:
      self.air_timer = 0
      self.vertical_velocity = 0
      self.movement[1] = 0
    else:
      self.air_timer += 1