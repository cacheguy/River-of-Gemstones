import arcade
import random
from constants import *

class Gem(arcade.Sprite): 
    def __init__(self, filename):
        super().__init__(filename=filename, scale=SCALE)
        self.left = SCREEN_WIDTH
        self.center_y = random.randint(self.height, SCREEN_HEIGHT-self.height)
        self.change_x = -5
        self.original_position = self.position
        self.collected = False
        self.score_value = 0
        self.collect_sound = arcade.sound.load_sound("src/assets/sounds/collect.wav")

    def on_update(self, delta_time):
        if self.collected:
            self.change_y = 3
            if self.alpha - 30 < 0: self.alpha = 0
            else: self.alpha -= 30
        else:
            if self.right < 0 or self.alpha <= 0:
                self.kill()
            elif self.collides_with_sprite(self.engine.boat) and not self.engine.boat.invincible: 
                self.collected = True
                self.engine.score += self.score_value*100
                self.engine.score += self.score_value*100*1.2*(self.left/SCREEN_WIDTH)
                self.collect_sound.play()
        

class Emerald(Gem):
    def __init__(self, *args, **kwargs):
        super().__init__("src/assets/images/gems/emerald.png", *args, **kwargs)
        self.score_value = 1

class Amethyst(Gem):
    def __init__(self, *args, **kwargs):
        super().__init__("src/assets/images/gems/amethyst.png", *args, **kwargs)
        self.score_value = 2

class Opal(Gem):
    def __init__(self, *args, **kwargs):
        super().__init__("src/assets/images/gems/opal.png", *args, **kwargs)
        self.score_value = 4

class Ruby(Gem):
    def __init__(self, *args, **kwargs):
        super().__init__("src/assets/images/gems/ruby.png", *args, **kwargs)
        self.score_value = 8

class Pearl(Gem):
    def __init__(self, *args, **kwargs):
        super().__init__("src/assets/images/gems/pearl.png", *args, **kwargs)
        self.score_value = 15

GEM_CHANCES = [
    (40, Emerald),
    (32, Amethyst),
    (17, Opal),
    (10, Ruby),
    (1, Pearl)
]

GEM_CHANCES_LIST = []
for value in GEM_CHANCES:
    for _ in range(value[0]):
        GEM_CHANCES_LIST.append(value[1])

def get_random_gem():
    return random.choice(GEM_CHANCES_LIST)