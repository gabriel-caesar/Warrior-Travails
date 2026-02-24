from random import randint, uniform
from entity import Entity

import pygame

# Main particles queue
particles_queue = []
 
class Particle(Entity):
  def __init__(self, direction: str, pos: list, color: str, factor: int):
    Entity.__init__(self, 10, pos)
    self.rect = pygame.Rect(pos[0], pos[1], randint(1, 4), randint(2, 4))
    self.direction = direction

    speed = uniform(0.6, 2) * factor
    self.movement = [speed if self.direction == 'right' else -speed, 0]
    self.color = color
    self.vanish_timer = 120

def blood_slash(entity: Entity, hit_from: int, blood_amount: int, squirt_factor: int, color: str) -> None:
  curr_direction = 'left' if hit_from == 1 else 'right'

  for _ in range(blood_amount):
    # Spawn offset is what makes the blood particles feel like a squirting liquid
    spawn_offset = randint(5, 12)
    midleft = [entity.rect.midleft[0] + spawn_offset, entity.rect.midleft[1]]
    midright = [entity.rect.midright[0] + spawn_offset, entity.rect.midright[1]]    
    spawn_point = list(midleft if hit_from == 1 else midright) # Originally a tuple
    p = Particle(curr_direction, spawn_point, color, squirt_factor)
    particles_queue.append(p)