from utils import TILE_SIZE, Tile
from random import randint

class Entity():
  def __init__(self, hp, pos):
    self.hp = hp
    self.pos = pos
    self.vertical_velocity = 0
    self.movement = [0, 0]
    self.air_timer = 0
    self.flip = False
    self.direction = 'right'
    self.guarding = False
    self.attacking = False
    self.attack_cooldown = 0

  def collision_test(self, obj_list):
    collision_list = []
    
    for obj in obj_list:
      if self.rect.colliderect(obj.rect):
        collision_list.append(obj)

    return collision_list

  def move(self, tile_list, enemies_list = []):
    collision_types = { "bottom": False, "top": False, "right": False, "left": False }

    # Dividing normal tiles from ramp tiles
    ramps = [t for t in tile_list if t.ramp]
    sq_tiles = [t for t in tile_list if not t.ramp]

    # If there are enemies to be tested collision with
    if enemies_list:
      world_tiles = [*sq_tiles, *enemies_list]     
    else:
      world_tiles = [*sq_tiles]

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


    return collision_types

  def attack(self, enemies_list):
    return
    # if self.attacking:

    #   # Loop through every enemy to find out which one is being attacked
    #   for defender in enemies_list:
    #     if self.rect.colliderect(defender.rect):
    #       print('Ahhhh, you\'ve attacked me!')
    #       defender.hp -= randint(14, 20)
