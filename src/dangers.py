import arcade
import random
from constants import *
from animations import Animation

class Danger(arcade.Sprite): 
    def __init__(self, filename):
        super().__init__(filename=filename, scale=SCALE)
        self.left = SCREEN_WIDTH
        self.center_y = random.randint(self.height, SCREEN_HEIGHT-self.height)
        
        self.original_position = self.position
        self.collided = False

    def on_update(self, delta_time):
        if self.right < 0 or self.top < 0 or self.bottom > SCREEN_HEIGHT: 
            self.kill()
        if self.collided:
            self.alpha -= 10
            self.angle += 8
            self.change_x = 2
        if self.alpha-10 < 0: self.kill()

    def get_hit_by_boat(self):
        self.collided = True

class Rock(Danger): 
    def __init__(self, *args, **kwargs):
        super().__init__(f"src/assets/images/dangers/rock{random.randint(1,3)}.png", *args, **kwargs)
        self.change_x = -3

class Piranha(Danger): 
    def __init__(self, *args, **kwargs):
        path = "src/assets/images/dangers/piranha"
        super().__init__(f"{path}1.png", *args, **kwargs)
        self.textures = [arcade.load_texture(f"{path}{i+1}.png") for i in range(3)]
        self.textures.append(self.textures[1])
        self.anim = Animation(self.textures, 0.26)
        self.change_x = random.randint(-17, -12)
        self.center_y = self.engine.boat.center_y

    def update_animation(self, delta_time):
        self.texture = self.anim.get_frame()
        self.anim.update(delta_time)

    def get_hit_by_boat(self):
        pass