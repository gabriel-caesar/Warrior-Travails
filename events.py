from __future__ import annotations
from typing import TYPE_CHECKING
from ui import UI

ui = UI(None)

if TYPE_CHECKING:
  from entity import Entity

event_queue = []

class CombatEvent():
  def __init__(self, entity: Entity):
    self.entity = entity
    self.vanish_timer = 60

class DamageEvent():
  def __init__(self, val: int, entity: Entity):
    CombatEvent.__init__(self, entity)
    self.val = val
    self.ui = ui.dmg_bubble(val, entity)
    

class BlockEvent():
  def __init__(self, entity: Entity):
    CombatEvent.__init__(self, entity)
    self.text = 'BLOCK'
    self.ui = ui.block_bubble(self.text, entity)