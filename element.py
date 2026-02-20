import pygame

from utils import load_image
from ui import UI

class Element(UI):
  def __init__(self, image_data: dict, text_data: dict, pos: tuple):
    UI.__init__(self, None)
    self.image = load_image(image_data['imgname'], image_data['subpath'])
    self.rect = self.image.get_rect(center = pos)
    self.text_data = text_data
    self.pos = pos
    self.text = self.create_text(self.text_data['size'], self.text_data['content'], self.text_data['color'])
    
    """
      Creates an element with a provided 
      image and with a centered text. Its
      `render()` function gives the ability
      to render the created element dynamically
    """

  def scale(self, double: bool = False, to: tuple | None = None) -> None:

    if double:
      self.image = pygame.transform.scale2x(self.image)
      self.rect = self.image.get_rect(center = self.pos)
    if to:
      self.image = pygame.transform.scale(self.image, to)
      self.rect = self.image.get_rect(center = self.pos)

  # def attachtext(self) -> None:
  #   self.create_text(self.text_data['size'], self.text_data['content'], self.text_data['color'])
    
  def render(self, screen: pygame.Surface) -> None:
    screen.blit(self.image, self.rect)
    screen.blit(self.text, self.text.get_rect(center = self.rect.center))