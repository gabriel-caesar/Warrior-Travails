from __future__ import annotations
from typing import TYPE_CHECKING

from utils import load_sprite_imgs, load_sound
from entity import Entity
from entitysound import EntitySound
import pygame

if TYPE_CHECKING:
    from utils import Tile
    from enemy import Enemy

# Animation imports
player_imgs = load_sprite_imgs(['player'])

class Player(pygame.sprite.Sprite, Entity, EntitySound):
  def __init__(self, hp: int, pos: list):
    pygame.sprite.Sprite.__init__(self)
    Entity.__init__(self, hp, pos)
    EntitySound.__init__(self, 'warrior')

    self.image = player_imgs['idle_1']
    self.rect = self.image.get_rect(midbottom = pos)
    self.mask = pygame.mask.from_surface(self.image)
    self.jump_pressed = False
    self.attack_cooldown = 0
    self.guard_cooldown = 0
    self.name = 'Warrior'

    self.setvolume(0.1) # Setting a standard volume for all sound effects

  def update(self, tile_list: list[Tile], enemies_list: list[Enemy]) -> None:

    self.animation_state = self.handle_animate_state()
    
    self.animate(player_imgs)

    self.combat(enemies_list)

    # Refreshes the guard and attack cooldown
    self.refresh_cooldown()

    # Gravity & collisions logic
    self.vertical_velocity += 1

    # If the space bar is held, the player falls slower 
    max_fall_velocity = 4 if self.jump_pressed else 15

    self.vertical_velocity = min(self.vertical_velocity, max_fall_velocity)
    self.movement[1] = self.vertical_velocity - 0.5
  
    # Don't count mob collision if dead
    collisions = self.move(tile_list, [] if self.dead_lock else enemies_list)

    if self.dead_lock:
      self.kill_entity()

    # If player collided with the ground, reset vertical_velocity and Y movement
    if collisions['bottom'] or collisions['top']:
      self.air_timer = 0
      self.vertical_velocity = 0
      self.movement[1] = 0
    else:
      self.air_timer += 1