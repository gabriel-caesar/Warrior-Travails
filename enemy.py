from utils import load_sprite_imgs
from entity import Entity
import pygame

class Enemy(pygame.sprite.Sprite, Entity):
  def __init__(self, name, hp, pos):
    pygame.sprite.Sprite.__init__(self)
    Entity.__init__(self, hp, pos)
    self.name = name

    if name == 'skeleton_1':
      enemy_imgs = load_sprite_imgs(['enemies', 'skeleton_1'])
      idle_1, walk_1 = enemy_imgs.values()

    self.animation_state = 'idle'
    self.animation_index = 0
    self.player_frames = []
    self.image = idle_1
    self.rect = self.image.get_rect(midbottom = (pos[0], pos[1]))
    self.mask = pygame.mask.from_surface(self.image)

  def update(self, tile_list):

    # Gravity & collisions logic
    self.vertical_velocity += 1
    self.vertical_velocity = min(self.vertical_velocity, 15)
    self.movement[1] = self.vertical_velocity - 0.5
  
    collisions = self.move(tile_list)

    # If player collided with the ground, reset vertical_velocity and Y movement
    if collisions['bottom'] or collisions['top']:
      self.air_timer = 0
      self.vertical_velocity = 0
      self.movement[1] = 0
    else:
      self.air_timer += 1
