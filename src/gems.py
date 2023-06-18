import arcade
import random
from constants import *

class Gem(arcade.Sprite): 
    def __init__(self, filename, previous_gem=None, seconds_passed=1, ):
        super().__init__(filename=filename, scale=SCALE)
        self.left = SCREEN_WIDTH
        if previous_gem is None:
            self.center_y = random.randint(self.height, SCREEN_HEIGHT-self.height)
        else:
            spawn = 865*seconds_passed
            self.center_y = random.randint(int(max(self.height, previous_gem.original_position[1]-spawn)),
                                           int(min(SCREEN_HEIGHT-self.height, previous_gem.original_position[1]+spawn)))
        self.change_x = -5
        self.original_position = self.position

    def on_update(self, delta_time):
        if self.right < 0: self.kill()

class Emerald(Gem):
    def __init__(self, *args, **kwargs):
        super().__init__("src/assets/images/gems/emerald.png", *args, **kwargs)

class Amethyst(Gem):
    def __init__(self, *args, **kwargs):
        super().__init__("src/assets/images/gems/amethyst.png", *args, **kwargs)

class Opal(Gem):
    def __init__(self, *args, **kwargs):
        super().__init__("src/assets/images/gems/opal.png", *args, **kwargs)

class Ruby(Gem):
    def __init__(self, *args, **kwargs):
        super().__init__("src/assets/images/gems/ruby.png", *args, **kwargs)

class Pearl(Gem):
    def __init__(self, *args, **kwargs):
        super().__init__("src/assets/images/gems/pearl.png", *args, **kwargs)

GEM_CHANCES = [
    (1, Emerald),
    (1, Amethyst),
    (1, Opal),
    (1, Ruby),
    (1, Pearl)
]

GEM_CHANCES_LIST = []
for value in GEM_CHANCES:
    for _ in range(value[0]):
        GEM_CHANCES_LIST.append(value[1])

def get_random_gem():
    return random.choice(GEM_CHANCES_LIST)