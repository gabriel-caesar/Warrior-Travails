from __future__ import annotations
from typing import TYPE_CHECKING

from events import DamageEvent, BlockEvent, event_queue
from utils import TILE_SIZE, SCREEN_X, Tile
from random import randint

if TYPE_CHECKING:
  from enemy import Enemy

import pygame

class Entity():
  def __init__(self, hp: int, pos: list):
    self.hp = hp
    self.max_hp = hp
    self.pos = pos

    self.vertical_velocity = 0
    self.movement = [0, 0]
    self.air_timer = 0
    self.flip = False
    self.direction = 'right'
    self.guarding = False

    # General attacking flags
    self.attacking = False
    self.attack_hitbox = ''

    # Animation locks
    self.attack_lock = False
    self.damage_lock = False
    self.dead_lock = False

    # Animation general
    self.animation_state = 'idle'
    self.animation_index = 0
    self.player_frames = []

    # When entity dies it has a timer to disappear
    self.vanish_timer = 200

  def collision_test(self, obj_list: list[Tile | Enemy]) -> list[Tile | Enemy]:
    collision_list = []
    
    for obj in obj_list:
      if self.rect.colliderect(obj.rect):
        collision_list.append(obj)

    return collision_list

  def move(self, tile_list: list[Tile], enemies_list: list[Enemy] = []) -> dict:
    collision_types = { "bottom": False, "top": False, "right": False, "left": False }

    # Dividing normal tiles from ramp tiles
    ramps = [t for t in tile_list if t.ramp]
    sq_tiles = [t for t in tile_list if not t.ramp and not t.platf]
    platform_tiles = [t for t in tile_list if t.platf]

    # If there are enemies to be tested collision with
    if enemies_list:
      world_tiles = [*sq_tiles, *enemies_list]     
    else:
      world_tiles = [*sq_tiles]

    # Handle out of bounds
    self.pos = self.out_of_bounds()

    if not self.attack_lock:
      # Collision handling for the X axis
      self.pos[0] += self.movement[0]
      self.rect.x = int(self.pos[0])
      collision_list = self.collision_test(world_tiles)
      
      for obj in collision_list:
        if self.movement[0] > 0:
          self.rect.right = obj.rect.left
          collision_types['right'] = True
        if self.movement[0] < 0:
          self.rect.left = obj.rect.right
          collision_types['left'] = True
        self.pos[0] = self.rect.x

      # Collision handling for the Y axis
      self.pos[1] += self.movement[1]
      self.rect.y = int(self.pos[1])
      collision_list = self.collision_test(world_tiles)

      for obj in collision_list:
        if self.movement[1] > 0:
          self.rect.bottom = obj.rect.top
          collision_types['bottom'] = True
        if self.movement[1] < 0:
          self.rect.top = obj.rect.bottom
          collision_types['top'] = True
        self.pos[1] = self.rect.y

    # Handling ramps
    for ramp in ramps:
      hitbox = ramp.rect

      # Check if the player collided with the ramp's bounding box
      if self.rect.colliderect(hitbox): 
        # Get player's relative position to the ramp X axis
        rel_x = self.rect.x - hitbox.x

        if ramp.ramp == 1: # Right facing ramp
          pos_height = rel_x + self.rect.width
        if ramp.ramp == 2: # Left facing ramp
          pos_height = TILE_SIZE - rel_x
          # y = h(height) - x

        # Constraints to avoid values overflow/underflow the tile size
        pos_height = min(pos_height, TILE_SIZE)
        pos_height = max(pos_height, 0)

        # Where the player rect's edge should stand along the ramp
        target_y = hitbox.y + TILE_SIZE - pos_height

        # If the player is overlapping the ramp
        if self.rect.bottom > target_y:
          self.rect.bottom = target_y
          self.pos[1] = self.rect.y

          collision_types['bottom'] = True

      # Handling jump through tiles
      for tile in platform_tiles:
        hitbox = tile.rect

        # Platform rects for collision need to be 5px tall (slightly big) so the program can 
        # read the collision, otherwise the player falls through it ignoring the collision
        platform_edge = pygame.Rect(hitbox.left, hitbox.top, hitbox.width, 5)
        player_edge = pygame.Rect(self.rect.left, self.rect.bottom, self.rect.width, 5)

        # The player only lands after the vertical velocity is positive
        # This means that while jumping through the platform, the velocity is still negative
        if player_edge.colliderect(platform_edge) and self.vertical_velocity > 0:
          self.rect.bottom = platform_edge.top
          self.pos[1] = self.rect.y
          collision_types['bottom'] = True

    return collision_types

  def animate(self, frames):

    # Destructuring the entity animation frames
    (
      attack_1, damage_1, damage_2,
      dead_1, dead_2, dead_3, 
      dead_4, dead_5, guard_1, 
      idle_1, jump_1, walk_1, 
      walk_2, walk_3, walk_4
    ) = frames.values()

    # Handling flipping logic
    self.flip = (self.direction == 'left')

    # == Lifecycle controlled animations ==
    if self.damage_lock and not self.attack_lock:
      self.player_frames = [ damage_1, damage_2 ]

    # == Lifecycle controlled animations ==
    elif self.attack_lock and not self.damage_lock:
      self.player_frames = [ walk_2, attack_1 ]

    # == Lifecycle controlled animations ==
    elif self.dead_lock:
      self.player_frames = [ dead_1, dead_2, dead_3, dead_4, dead_5 ]

    # == Input controlled animations ==
    else:
      match self.animation_state:
         
        case 'run': self.player_frames = [ walk_1, walk_2, walk_3, walk_4 ]

        case 'guard': self.player_frames = [ guard_1 ]

        case 'jump': self.player_frames = [ jump_1 ]

        case 'idle': self.player_frames = [ idle_1 ]
        
    self.animation_index += 0.1

    if (self.animation_index > len(self.player_frames)):
      self.animation_index = 0

      # If animation was locked by damage
      if self.damage_lock:
        self.damage_lock = False
        self.animation_state = 'idle'

      # If animation was locked by attack
      elif self.attack_lock:
        self.attack_lock = False
        self.animation_state = 'idle'

      elif self.dead_lock:
        self.animation_index = len(self.player_frames) - 1

    self.image = pygame.transform.flip(self.player_frames[int(self.animation_index)], self.flip, False)

    # Refreshing the rect only if the entity is dying
    if self.player_frames[0] == dead_1:
      self.rect = self.image.get_rect(midbottom = (self.pos[0], self.pos[1]))
      

  def combat(self, enemies_list: list[Enemy]) -> None:
    if self.attacking:      
      # Handling the swing sounds
      swingsounds = self.sounds['swingsound']
      swingindex = randint(0, len(swingsounds) - 1)
      swingsounds[swingindex].play()

      hit_from = 0 # 0 -> None; 1 -> Left; 2 -> Right

      # Attack hitbox dimensions
      attack_width = 16 
      attack_height = 32

      # Rendering the player's attack hitbox based on the player's direction
      if self.direction == 'right':
        self.attack_hitbox = pygame.Rect(self.pos[0], self.pos[1], attack_width, attack_height)
        self.attack_hitbox.left = self.rect.right
        hit_from = 2
        
      if self.direction == 'left':
        self.attack_hitbox = pygame.Rect(self.pos[0], self.pos[1], attack_width, attack_height)
        self.attack_hitbox.right = self.rect.left
        hit_from = 1


      # Loop through every enemy to find out which one is being attacked
      for defender in enemies_list:
        # Combatents facing the opposite direction and defender is guarding
        defending = self.direction != defender.direction and defender.guarding

        if self.attack_hitbox.colliderect(defender.rect) and not defender.dead_lock and not defending:
          self.attack(defender, hit_from)
          
        if self.attack_hitbox.colliderect(defender.rect) and defending:
          self.defend(defender, hit_from)

    else:
      # Clear the attack hitbox if the entity is not attacking
      self.attack_hitbox = ''

  def attack(self, defender: Entity, hit_from: int) -> None:
    # Handling damage animation
    defender.animation_state = 'damage'
    defender.damage_lock = True
    defender.animation_index = 0

    # Take damage
    dmg = DamageEvent(randint(14, 20), defender, hit_from)
    defender.hp -= dmg.val
    event_queue.append(dmg)

    # Handle defender's death
    if defender.hp <= 0: 
      defender.sounds['deathsound'].play()
      defender.dead_lock = True
      return
    else:
      damagesounds = defender.sounds['damagesound']
      dmgindex = randint(0, len(damagesounds) - 1)
      damagesounds[dmgindex].play()
    
  def defend(self, defender: Entity, hit_from: int) -> None:
    defender.sounds['blocksound'].play()
    defender.guard_cooldown = 120
    defender.guarding = False
    block = BlockEvent(defender, hit_from)
    event_queue.append(block)

  def refresh_cooldown(self) -> None:
    # General cooldown control
    if self.attack_cooldown > 0:
      self.attack_cooldown -= 1
      self.attacking = False
    if self.guard_cooldown > 0:
      self.guard_cooldown -= 1


  def kill_entity(self) -> None:
    if self.vanish_timer == -10:
      self.kill()
    else:
      self.vanish_timer -= 1

  # For enemies
  def get_direction(self) -> str:
    if self.movement[0] > 0:
      return 'right'
    if self.movement[0] < 0:
      return 'left'
    
  def out_of_bounds(self) -> list:
    updated_pos = self.pos

    if self.movement[0] > 0:
      if self.rect.right >= SCREEN_X:
        updated_pos[0] = SCREEN_X - 30 # offset

    elif self.movement[0] < 0:
      if self.rect.left <= 0:
        updated_pos[0] = 0

    return updated_pos

  def handle_animate_state(self) -> str:
     # Handling animation state
    if self.air_timer > 3:
      return 'jump'

    elif self.attacking:
      # Attack lock to run the full attack animation
      self.attack_lock = True
      return 'attack'

    elif self.movement[0] != 0 and not self.attacking:
      return 'run'

    elif self.guarding:
      return 'guard'

    else:
      return 'idle'
    
  
  def draw(self, surface: pygame.Surface) -> None:
    offset = pygame.Vector2(0, 0)

    # Attacking animation takes 2 frames.
    # So, if the first frame has been passed, offset the player
    # to prevent broken animation
    if (self.attack_lock and 
        self.direction == "left" and 
        self.animation_index > 1 and
        not self.damage_lock):
      
      offset = pygame.Vector2(-12, 0)

    surface.blit(self.image, self.rect.topleft + offset)