import arcade
from constants import *
from animations import Animation
from math import sin
from pyglet.math import Vec2

def lerp(value1, value2, alpha):
    return value1 + (alpha * (value2 - value1))

class Boat(arcade.Sprite):
    def __init__(self):
        super().__init__(scale=SCALE)
        self.textures = [arcade.load_texture(f"src/assets/images/boat/boat_idle{i+1}.png") for i in range(4)]
        self.textures.append(self.textures[2])
        self.textures.append(self.textures[1])
        self.texture = self.textures[0]
        self.idle_anim = Animation(self.textures, 0.15)
        self.hit_box
        self.left = 160
        self.center_y = SCREEN_HEIGHT/2
        self.frames_passed = 0

    def on_update(self, delta_time):
        self.frames_passed += 1

        max_speed = 12
        acceleration = 0.55
        friction = 0.55
        keys_pressed = False
        if self.engine.up_pressed and not self.engine.down_pressed:
            self.change_y += acceleration
            angle_speed = 16
            keys_pressed = True
        elif self.engine.down_pressed and not self.engine.up_pressed:
            self.change_y -= acceleration
            angle_speed = -16
            keys_pressed = True
        else:
            if self.change_y > 0: 
                self.change_y -= friction
                if self.change_y < 0:
                    self.change_y = 0
            elif self.change_y < 0:
                self.change_y += friction
                if self.change_y > 0:
                    self.change_y = 0
            angle_speed = 0

        self.change_y = max(min(self.change_y, max_speed), -max_speed)
        if self.change_y == 0 and not keys_pressed:
            self.angle = sin(self.frames_passed/15)*6
        else:
            self.angle = lerp(self.angle, angle_speed, 0.18)
            self.frames_passed = 0

        self.bottom = min(self.bottom, SCREEN_HEIGHT)
        self.top = max(self.top, 0)

    def update_animation(self, delta_time):
        self.texture = self.idle_anim.get_frame()
        self.idle_anim.update(delta_time)