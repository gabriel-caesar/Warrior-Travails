import pygame
from os import path, listdir

TILE_SIZE = 32
SCREEN_X = 1400
SCREEN_Y = 640

class Tile():
  def __init__(self, rect: pygame.Rect, ramp: int = 0, platf: bool = False): # 0 == none, 1 == right and 2 == left
    self.rect = rect
    self.ramp = ramp
    self.platf = platf

def load_image(imgname: str, subpath: list) -> pygame.Surface:
  try:
    base = path.dirname(__file__)
    imgpath = path.join(base, *subpath, imgname)
    return pygame.image.load(imgpath)
  except FileNotFoundError:
    raise FileNotFoundError(f'\n\nFile -># {imgname} #<- was not found in the provided subpath\n')

def load_sprite_imgs(directory: list, exception: str | None = None) -> dict[str: pygame.Surface]:
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

def build_tile_list(raw_list: list) -> list[Tile]:
  new_tile_list = []

  for y in range(len(raw_list)):
    for x in range(len(raw_list[y])):
      tile = ''

      # Skipping the walkthrough-walls
      if raw_list[y][x] != 0  and raw_list[y][x] != 14 and raw_list[y][x] != 74:

        if raw_list[y][x] == 67: # Ramp number types
          tile = Tile(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        elif raw_list[y][x] == 4: # Platform number types
          tile = Tile(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 0, True)
        else:
          tile = Tile(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 0)

        new_tile_list.append(tile)

  return new_tile_list