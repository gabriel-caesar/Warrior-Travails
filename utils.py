import pygame
from os import path, listdir

TILE_SIZE = 32

class Tile():
  def __init__(self, rect, ramp = 0): # 0 == none, 1 == right and 2 == left
    self.rect = rect
    self.ramp = ramp

def load_image(imgname, subpath):
  base = path.dirname(__file__)
  imgpath = path.join(base, *subpath, imgname)
  return pygame.image.load(imgpath)

def load_sprite_imgs(directory, exception = None):
  # Getting all files from the current directory (/graphics/directory)
  base = path.dirname(__file__)
  imgpath = path.join(base, 'graphics', *directory)
  files = listdir(imgpath)

  sheet = {}

  for file in files:

    if file == exception:
      pass

    else:
      frame_name = list(filter(lambda x: x != 'png', file.split('.')))
      frame_name = frame_name[0]

      img_surf = load_image(file, ['graphics', *directory])
      sheet[frame_name] = img_surf

  return sheet

def build_tile_list(raw_list):
  new_tile_list = []

  for y in range(len(raw_list)):
    for x in range(len(raw_list[y])):
      tile = ''

      # Skipping the walkthrough-walls
      if raw_list[y][x] != 0 and raw_list[y][x] != 14 and raw_list[y][x] != 74:

        if raw_list[y][x] == 67: # Ramp number types
          tile = Tile(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        else:
          tile = Tile(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 0)

        new_tile_list.append(tile)

  return new_tile_list