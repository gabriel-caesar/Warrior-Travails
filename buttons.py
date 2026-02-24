from element import Element
from ui import COLOR_2, Slider
from utils import SCREEN_X, load_sound

def get_menu_ui() -> tuple:
  button_sound = load_sound('click1.wav', ['sound', 'ui'])

  # Creating the game title text
  title_imgdata = { 'imgname': 'header_art.png', 'subpath': ['graphics', 'ui', 'menu'] }
  title_textdata =  { 'size': 20, 'content': 'Warrior Travails', 'color': COLOR_2}
  title_pos = (SCREEN_X // 2, 200) 

  game_title = Element(title_imgdata, title_textdata, title_pos)
  game_title.scale(double = True)

  # New game button option
  newgame_imgdata = { 'imgname': 'button_1.png', 'subpath': ['graphics', 'ui', 'menu'] }
  newgame_textdata = { 'size': 14, 'content': 'New Game', 'color': COLOR_2 }
  newgame_pos = (SCREEN_X // 2, 300)

  newgame_button = Element(newgame_imgdata, newgame_textdata, newgame_pos, button_sound)

  # Options button option
  options_imgdata = { 'imgname': 'button_1.png', 'subpath': ['graphics', 'ui', 'menu'] }
  options_textdata = { 'size': 14, 'content': 'Options', 'color': COLOR_2 }
  options_pos = (SCREEN_X // 2, 360)

  options_button = Element(options_imgdata, options_textdata, options_pos, button_sound)

  # back button option
  quit_imgdata = { 'imgname': 'button_1.png', 'subpath': ['graphics', 'ui', 'menu'] }
  quit_textdata = { 'size': 14, 'content': 'Quit', 'color': COLOR_2 }
  quit_pos = (SCREEN_X // 2, 420)

  quit_button = Element(quit_imgdata, quit_textdata, quit_pos, button_sound)

  return (game_title, newgame_button, options_button, quit_button)

def get_options_ui(music_volume: float) -> tuple:
  button_sound = load_sound('click1.wav', ['sound', 'ui'])

  # Options header title
  options_imgdata = { 'imgname': 'header_art.png', 'subpath': ['graphics', 'ui', 'menu'] }
  options_textdata =  { 'size': 20, 'content': 'Options', 'color': COLOR_2}
  options_pos = (SCREEN_X // 2, 100) 

  game_options = Element(options_imgdata, options_textdata, options_pos)
  game_options.scale(double = True)

  # Options frame
  frame_imgdata = { 'imgname': 'frame.png', 'subpath': ['graphics', 'ui', 'menu'] }
  frame_pos = (SCREEN_X // 2, 320)
  frame = Element(frame_imgdata, None, frame_pos)
  frame.scale(to = (game_options.rect.width, frame.rect.height * 1.5))

  # Music volume slider
  slider_pos = (frame.rect.left + 60, frame.rect.top + 80)
  music_slider = Slider(slider_pos, music_volume)
  music_slider.sound = button_sound
  music_slider.text = music_slider.create_text(14, 'Music Volume', COLOR_2)

  # Quit button option
  back_imgdata = { 'imgname': 'button_1.png', 'subpath': ['graphics', 'ui', 'menu'] }
  back_textdata = { 'size': 14, 'content': 'Back', 'color': COLOR_2 }
  back_pos = (SCREEN_X // 2, 520)

  back_button = Element(back_imgdata, back_textdata, back_pos, button_sound)
  return (back_button, game_options, frame, music_slider)