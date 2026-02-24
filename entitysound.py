from utils import load_sound, load_allsounds

class EntitySound():
  def __init__(self, ename: str):
    self.sounds = {
      'swingsound': load_allsounds('swing', ['sound', 'entities'], ename),
      'damagesound': load_allsounds('damage', ['sound', 'entities'], ename),
      'deathsound': load_sound('death.wav', ['sound', 'entities', ename]),
      'jumpsound': load_allsounds('jump', ['sound', 'entities'], ename),
      'blocksound': load_sound('block.wav', ['sound', 'entities', ename])
    }

  def setvolume(self, val: float) -> None:
    for _, sound in self.sounds.items():
      if isinstance(sound, list): # If the following topic sound is a list of sounds
        for s in sound:
          s.set_volume(val)
      else:
        sound.set_volume(val)