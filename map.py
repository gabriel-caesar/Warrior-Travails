from os import path
import json
from utils import load_sprite_imgs

# Importing the world images
world_imgs = load_sprite_imgs(['world'], 'bg.png')
(
  dirt_1, dirt_2, grass_1,
  grass_2, lava_1, lava_2,
  ramp_1, rock_1, rock_2
) = world_imgs.values()

def generate_map():
  base = path.dirname(__file__)
  absolute = path.join(base, 'assets', 'map', 'map_1.tmj')
  tile_type_list = []
  with open(absolute) as f:
    json_map = json.loads(f.read())
    tile_type_list = json_map['layers'][0]['data']
  
  counter = 0
  row = []
  map_list = []

  # Generating a 2D list to give me a (x,y) value of each tile
  for n in range(len(tile_type_list)):
    row.append(tile_type_list[n])
    counter += 1
    if counter == 44:
      map_list.append(row)
      row = []
      counter = 0
  
  return map_list


def draw_map(list, surf, tile_size):
  for y in range(len(list)):
    for x in range(len(list[y])):
      if list[y][x] != 0:
        match list[y][x]:

          case 1:
            surf.blit(grass_1, (x * tile_size, y * tile_size))
          case 12:
            surf.blit(dirt_1, (x * tile_size, y * tile_size))
          case 71:
            surf.blit(rock_1, (x * tile_size, y * tile_size))
          case 74:
            surf.blit(rock_2, (x * tile_size, y * tile_size))
          case 38:
            surf.blit(lava_1, (x * tile_size, y * tile_size))
          case 28:
            surf.blit(lava_2, (x * tile_size, y * tile_size))
          case 14:
            surf.blit(dirt_2, (x * tile_size, y * tile_size))
          case 4:
            surf.blit(grass_2, (x * tile_size, y * tile_size))
          case 67:
            surf.blit(ramp_1, (x * tile_size, y * tile_size))