from __future__ import annotations
from typing import TYPE_CHECKING

from utils import load_sprite_imgs, load_image
from entitysound import EntitySound
from entity import Entity
from random import randint
import pygame

if TYPE_CHECKING:
  from player import Player

# Animation dict
enemy_imgs = {}

# Flags
aggro_tolerance_zone = 50

# Symbol that will show on top of an aggro'd creature
aggro_pointer = load_image('aggro_pointer.png', ['graphics', 'enemies'])

class Enemy(pygame.sprite.Sprite, Entity, EntitySound):
  def __init__(self, name: str, hp: int, pos: list):
    pygame.sprite.Sprite.__init__(self)
    Entity.__init__(self, hp, pos)
    self.name = name

    if name == 'skeleton_1':
      global enemy_imgs
      enemy_imgs = load_sprite_imgs(['enemies', 'skeleton_1'])
      # Audio for skeletons
      EntitySound.__init__(self, 'skeleton')

    self.image = enemy_imgs['idle_1']
    self.rect = self.image.get_rect(midbottom = pos)
    self.mask = pygame.mask.from_surface(self.image)

    self.aggro = (False, False)
    self.patrol_index = randint(12, 94) # Random patrol behaviors, less robotic pattern
    self.patrol_factor = 1
    self.attack_cooldown = 60
    self.guard_cooldown = 60

    self.setvolume(0.1) # Setting a standard volume for all sound effects

  def patrol(self, collisions: dict) -> None:

    if not self.dead_lock and not self.damage_lock:
      # Smooth walking step
      walking_step = 0.05
      
      # Patrol to the right
      if self.patrol_index == 120 or collisions['left']:
        self.patrol_index = 120 # Resets the patrol index if a collision turned the enemy before 120
        self.patrol_factor = -1
        

      # Patrol to the left
      if self.patrol_index == 0 or collisions['right']:
        self.patrol_index = 0 # Resets the patrol index if a collision turned the enemy before 0
        self.patrol_factor = 1

      # If walking SMOOTHLY left
      if self.patrol_factor == 1:
        self.movement[0] += walking_step
        if self.movement[0] > 0.8:
          self.movement[0] = 0.8

      # If walking SMOOTHLY right
      elif self.patrol_factor == -1:
        self.movement[0] -= walking_step
        if self.movement[0] < -0.8:
          self.movement[0] = -0.8

      # Increment the index
      self.patrol_index += self.patrol_factor
    else:
      # If aggro was activated or enemy died or got damaged, stop moving
      self.movement[0] = 0
      # Resets the patrol index if aggro was activated so it
      # can return to patrol seamlessly after losing the aggro state
      self.patrol_index = 120 if self.direction == 'left' else 0
    
  def get_aggro(self, player: Player) -> tuple:

    if not self.dead_lock:

      # Aggro rects
      aggro_rect_1 = pygame.Rect(self.rect.left, 
                            self.rect.top, 
                            self.rect.width + aggro_tolerance_zone, 
                            self.rect.height)
      aggro_rect_2 = pygame.Rect(self.rect.left, 
                            self.rect.top, 
                            self.rect.width + aggro_tolerance_zone, 
                            self.rect.height)

      # Attaching the aggro rects to the player's rect edges      
      aggro_rect_1.right = self.rect.left
      aggro_rect_2.left = self.rect.right

      aggroed_left = aggro_rect_1.colliderect(player.rect) and not player.dead_lock
      aggroed_right = aggro_rect_2.colliderect(player.rect) and not player.dead_lock

      return aggroed_left, aggroed_right

    # If enemy is dead, no aggro is created
    return False, False

    
  def chase_player(self, player: Player, screen: pygame.Surface) -> None:

    # Attack hitbox dimensions
    attack_length = 14

    # Render the aggro pointer on top of the enemy
    aggro_pointer_rect = aggro_pointer.get_rect(midbottom = self.rect.midtop)
    aggro_pointer_rect.top -= 10
    screen.blit(aggro_pointer, aggro_pointer_rect)

    # Serves the purpose of letting the enemy know when to call self.attack()
    can_atk_l = player.rect.right >= self.rect.left - attack_length and player.rect.right <= self.rect.left
    can_atk_r = player.rect.left <= self.rect.right + attack_length and player.rect.left >= self.rect.right

    # Smooth chasing step
    chase_step = 0.1

    # Destructuring the aggro directions
    aggroed_left, aggroed_right = self.aggro

    # Smoothly chase left
    if aggroed_left:
      self.movement[0] -= chase_step
      if self.movement[0] < -1:
        self.movement[0] = -1

    # Smoothly chase right
    elif aggroed_right:
      self.movement[0] += chase_step
      if self.movement[0] > 1:
        self.movement[0] = 1 

    # If enemy can attack
    if can_atk_l or can_atk_r:
      self.refresh_cooldown()
      self.movement[0] = 0
      if self.attack_cooldown == 0:
        self.attacking = True
        self.combat([ player ]) # So the function can iterate through a list
        self.attack_cooldown = 60

  def update(self, tile_list: list, player: Player, screen: pygame.Surface) -> None:
    # Gravity & collisions logic
    self.vertical_velocity += 1
    self.vertical_velocity = min(self.vertical_velocity, 15)
    self.movement[1] = self.vertical_velocity - 0.5

    # Assign the according animation state to the animation_state flag
    self.animation_state = self.handle_animate_state()

    self.animate(enemy_imgs)
  
    collisions = self.move(tile_list)

    self.aggro = self.get_aggro(player)

    self.direction = self.get_direction()

    if self.aggro[0] or self.aggro[1]:
      self.chase_player(player, screen)
    else:
      self.patrol(collisions)
      self.attacking = False # Helps the bot to not get stuck in the attacking animation
    
    if self.dead_lock:
      self.kill_entity()

    # If player collided with the ground, reset vertical_velocity and Y movement
    if collisions['bottom'] or collisions['top']:
      self.air_timer = 0
      self.vertical_velocity = 0
      self.movement[1] = 0
    else:
      self.air_timer += 1