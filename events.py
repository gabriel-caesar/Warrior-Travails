from __future__ import annotations
from typing import TYPE_CHECKING
from ui import UI

ui = UI(None)

if TYPE_CHECKING:
  from entity import Entity

# Main event queue list
event_queue = []

class CombatEvent():
  def __init__(self, entity: Entity, hit_from: int):
    self.entity = entity
    self.vanish_timer = 60
    self.spawned_particles = False
    self.hit_from = hit_from

class DamageEvent():
  def __init__(self, val: int, entity: Entity, hit_from: int):
    CombatEvent.__init__(self, entity, hit_from)
    self.val = val
    self.ui = ui.dmg_bubble(val, entity)

class BlockEvent():
  def __init__(self, entity: Entity, hit_from):
    CombatEvent.__init__(self, entity, hit_from)
    self.text = 'BLOCK'
    self.ui = ui.block_bubble(self.text, entity)