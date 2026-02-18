from __future__ import annotations
from typing import TYPE_CHECKING
from ui import UI

ui = UI(None)

if TYPE_CHECKING:
  from entity import Entity

event_queue = []

class DamageEvent():
  def __init__(self, val: int, entity: Entity):
    self.val = val
    self.entity = entity
    self.vanish_timer = 60
    self.ui = ui.dmg_bubble(val, entity)
