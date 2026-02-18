from __future__ import annotations
from typing import TYPE_CHECKING

import pygame
from os import path

if TYPE_CHECKING:
  from player import Player
  from entity import Entity

COLOR_1 = '#050b24'
COLOR_2 = '#F8A845'
COLOR_3 = '#950A0A'

def get_font(size: int) -> pygame.Font:
  base = path.dirname(__file__)
  fontpath = path.join(base, 'font/PressStart2P-Regular.ttf')
  return pygame.font.Font(fontpath, size)

class UI():
  def __init__(self, surf: pygame.Surface):
    self.screen = surf
  
  def unit_hpbar(self, entity: Entity, color: str = '') -> None:
    bar_width = entity.rect.width + 10
    bar_height = 10

    # Dynamically calculates how much life to be shown on the health bar
    ratio = entity.max_hp / bar_width
    filler_width = entity.hp / ratio

    # If there is a color preference
    filler_color = COLOR_3
    if color: 
      filler_color = color

    hpbar_wrapper = pygame.Rect(entity.pos[0], entity.pos[1], bar_width, bar_height)
    hpbar_filler = pygame.Rect(entity.pos[0], entity.pos[1], filler_width, bar_height)
    hpbar_border = pygame.Rect(entity.pos[0], entity.pos[1], bar_width, bar_height)

    hpbar_wrapper.bottomleft = entity.rect.topleft 
    hpbar_filler.bottomleft = entity.rect.topleft 
    hpbar_border.bottomleft = entity.rect.topleft 

    pygame.draw.rect(
      self.screen, 
      COLOR_1,
      hpbar_wrapper,
    )
    pygame.draw.rect(
      self.screen, 
      filler_color,
      hpbar_filler,
    )
    pygame.draw.rect(
      self.screen, 
      COLOR_2,
      hpbar_border,
      2
    )

  def create_text(self, font_size: int, content: str, color: str) -> pygame.Surface:
    text_font = get_font(font_size)
    text_content = content
    text_surf = text_font.render(text_content, False, color)

    return text_surf

  def player_hpbar(self, player: Player) -> None:
    bar_height = 40
    bar_width = 400
    bar_pos = 20

    # Dynamically calculates how much life to be shown on the health bar
    ratio = player.max_hp / bar_width
    filler_width = player.hp / ratio

    # Creating the bar rectangles
    hpbar_wrapper = pygame.Rect(bar_pos, bar_pos, bar_width, bar_height)
    hpbar_filler = pygame.Rect(bar_pos, bar_pos, filler_width, bar_height)
    hpbar_border = pygame.Rect(bar_pos, bar_pos, bar_width, bar_height)

    # HP bar text
    hp_content = f'{str(player.hp)}/{str(player.max_hp)}'
    hp_text = self.create_text(25, hp_content, COLOR_2)

    # HP header text
    hp_header_content = 'Warrior health bar'
    hp_header_text = self.create_text(15, hp_header_content, COLOR_1)

    pygame.draw.rect(
      self.screen, 
      COLOR_1,
      hpbar_wrapper,
    )
    pygame.draw.rect(
      self.screen, 
      COLOR_3,
      hpbar_filler,
    )
    pygame.draw.rect(
      self.screen, 
      COLOR_2,
      hpbar_border,
      2
    )

    # Renders the text in the middle of the HP bar
    self.screen.blit(hp_text, hp_text.get_rect(center = hpbar_wrapper.center))
    self.screen.blit(hp_header_text, hp_header_text.get_rect(bottomleft = hpbar_border.topleft))

  def create_icon(self, icon: pygame.Surface, key_pressed: bool, key: str, cooldown: int, pos: tuple) -> None:
    # Icon UI essentials
    lp, tp = pos
    icon_img = icon
    icon_rect = icon.get_rect(left = lp, top = tp)

    # Cooldown text
    cooldown_content = str(cooldown // 30)
    cooldown_number = self.create_text(20, cooldown_content, COLOR_2)

    # More icon UI
    p = 10 # Padding
    icon_border = pygame.Rect(icon_rect.left, icon_rect.top, icon_rect.width + p, icon_rect.height + p)
    icon_border.center = icon_rect.center # Centering the rect after the padding
    icon_bg = pygame.Rect(icon_rect.left, icon_rect.top, icon_rect.width + p, icon_rect.height + p)
    icon_bg.center = icon_rect.center # Centering the rect after the padding

    # Creates and renders the key to be associated with the icon
    self.create_key(key_pressed, key, lp, tp, icon_rect)

    # Renders the icon
    pygame.draw.rect(self.screen, COLOR_1, icon_bg)
    self.screen.blit(icon_img.convert_alpha(), icon_rect)
    pygame.draw.rect(self.screen, COLOR_2, icon_border, 2)

    if cooldown:
      # Renders a opaque rect and the cooldown timer
      overlay = pygame.Surface(icon_bg.size, pygame.SRCALPHA) # pygame.SRCALPHA enables per-pixel alpha
      overlay.fill((0, 0, 0, 128))  # 50% opacity
      self.screen.blit(overlay, icon_bg) 
      self.screen.blit(cooldown_number, cooldown_number.get_rect(center = icon_rect.center))
  
  def create_key(self, key_pressed: bool, key: str, icon_left: int, icon_top: int, icon_rect: pygame.Rect) -> None:
    icon_key = self.create_text(20, key, COLOR_1 if key_pressed else COLOR_2)
    mt = 75
    icon_key_rect = icon_key.get_rect(center = (icon_left + (icon_rect.width // 2), icon_top + mt))
    
    icon_key_border = pygame.Rect(icon_key_rect.left, icon_key_rect.top, icon_key_rect.width + 8, icon_key_rect.height + 8)
    icon_key_border.center = icon_key_rect.center

    icon_key_bg = pygame.Rect(icon_key_rect.left, icon_key_rect.top, icon_key_rect.width + 8, icon_key_rect.height + 8)
    icon_key_bg.center = icon_key_rect.center

    # Renders the attack key
    pygame.draw.rect(self.screen, COLOR_2 if key_pressed else COLOR_3, icon_key_bg)
    self.screen.blit(icon_key, icon_key_rect)
    pygame.draw.rect(self.screen, COLOR_3 if key_pressed else COLOR_2, icon_key_border, 2)

  def dmg_bubble(self, val: int, entity: Entity) -> tuple:

    dmg_surf = self.create_text(10, str(val), COLOR_2 if entity.name == 'Warrior' else COLOR_3)
    text_rect = dmg_surf.get_rect(midbottom = entity.rect.midtop)
    
    return dmg_surf, text_rect
