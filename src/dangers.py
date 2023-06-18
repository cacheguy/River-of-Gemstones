import arcade
import random
from constants import *
from animations import Animation

class Danger(arcade.Sprite): 
    def __init__(self, filename, previous_gem=None):
        super().__init__(filename=filename, scale=SCALE)
        self.left = SCREEN_WIDTH

        # Try not to be in a gem's path
        for _ in range(12):
            self.center_y = random.randint(self.height, SCREEN_HEIGHT-self.height)
            if previous_gem is None: break
            top = previous_gem.original_position[1]+previous_gem.height/2 
            bottom = previous_gem.original_position[1]-previous_gem.height/2
            if not ((self.bottom < top and self.bottom > bottom) or (self.top < bottom and self.top > top)):
                break
        
        self.original_position = self.position

    def on_update(self, delta_time):
        if self.right < 0: 
            self.kill()

class Rock(Danger): 
    def __init__(self, *args, **kwargs):
        super().__init__(f"src/assets/images/dangers/rock{random.randint(1,3)}.png", *args, **kwargs)
        self.change_x = -3.2

class Piranha(Danger): 
    def __init__(self, *args, **kwargs):
        path = "src/assets/images/dangers/piranha"
        super().__init__(f"{path}1.png", *args, **kwargs)
        self.textures = [arcade.load_texture(f"{path}{i+1}.png") for i in range(3)]
        self.textures.append(self.textures[1])
        self.anim = Animation(self.textures, 0.26)
        self.change_x = -6

    def update_animation(self, delta_time):
        self.texture = self.anim.get_frame()
        self.anim.update(delta_time)