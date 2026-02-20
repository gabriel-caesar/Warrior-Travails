from __future__ import annotations
from typing import TYPE_CHECKING

from utils import load_sprite_imgs, load_image
from entity import Entity
import pygame

if TYPE_CHECKING:
  from player import Player

# Animation dict
enemy_imgs = {}

# Flags
aggro_tolerance_zone = 50

# Symbol that will show on top of an aggro'd creature
aggro_pointer = load_image('aggro_pointer.png', ['graphics', 'enemies'])

class Enemy(pygame.sprite.Sprite, Entity):
  def __init__(self, name: str, hp: int, pos: list):
    pygame.sprite.Sprite.__init__(self)
    Entity.__init__(self, hp, pos)
    self.name = name

    if name == 'skeleton_1':
      global enemy_imgs
      enemy_imgs = load_sprite_imgs(['enemies', 'skeleton_1'])

    self.image = enemy_imgs['idle_1']
    self.rect = self.image.get_rect(midbottom = pos)
    self.mask = pygame.mask.from_surface(self.image)

    self.aggro = False
    self.patrol_index = 0
    self.patrol_factor = -1
    self.attack_cooldown = 60
    self.guard_cooldown = 60

  def patrol(self, collisions: dict) -> None:

    if not self.dead_lock and not self.damage_lock:
      
      # Patrol to the right
      if self.patrol_index == 120 or collisions['left']:

        self.patrol_index = 120 # Resets the patrol index if a collision turned the enemy before 120
        self.patrol_factor = -1
        self.movement[0] = 0.5

      # Patrol to the left
      if self.patrol_index == 0 or collisions['right']:

        self.patrol_index = 0 # Resets the patrol index if a collision turned the enemy before 0
        self.patrol_factor = 1
        self.movement[0] = -0.5

      # Increment the index
      self.patrol_index += self.patrol_factor
    else:
      # If aggro was activated or enemy died or got damaged, stop moving
      self.movement[0] = 0
      # Resets the patrol index if aggro was activated so it
      # can return to patrol seamlessly after losing the aggro state
      self.patrol_index = 120 if self.direction == 'left' else 0
    
  def get_aggro(self, player: Player) -> bool:

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
      
      aggro_rect_1.right = self.rect.left
      aggro_rect_2.left = self.rect.right

      if aggro_rect_1.colliderect(player.rect) and not player.dead_lock:
        self.movement[0] = -1 # Move left
        return True
      elif aggro_rect_2.colliderect(player.rect) and not player.dead_lock:
        self.movement[0] = 1 # Move right
        return True

    return False

    
  def chase_player(self, player: Player, screen: pygame.Surface) -> None:

    # Attack hitbox dimensions
    attack_length = 14

    # Render the aggro pointer on top of the enemy
    aggro_pointer_rect = aggro_pointer.get_rect(midbottom = self.rect.midtop)
    screen.blit(aggro_pointer, aggro_pointer_rect)

    # Serves the purpose of letting the enemy know when to call self.attack()
    can_atk_l = player.rect.right >= self.rect.left - attack_length and player.rect.right <= self.rect.left
    can_atk_r = player.rect.left <= self.rect.right + attack_length and player.rect.left >= self.rect.right

    if self.direction == 'left':
      self.movement[0] = -1
    elif self.direction == 'right':
      self.movement[0] = 1

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

    if self.aggro:
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