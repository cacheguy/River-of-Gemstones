import arcade
from constants import *
from animations import Animation
from math import sin
from time import time
import dangers

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
        self.fireball_old_time = time()
        self.fireball_new_time = 0
        self.stunned = 0
        self.stun_anim_timer = 0
        self.invincible_anim_timer = 0
        self.invincible_old_time = 0
        self.invincible = False
        self.hurt_sound = arcade.sound.load_sound("src/assets/sounds/hurt.wav")
        self.fireball_sound = arcade.sound.load_sound("src/assets/sounds/fireball.wav")

    def on_update(self, delta_time):
        if self.stunned>0:
            spin_speed = 11
            if self.stunned+spin_speed>359: 
                self.stunned = 0
                self.angle += self.stunned+spin_speed-359
                self.invincible = True
                self.invincible_old_time = time()
            else:
                self.stop()
                self.center_x -= 6
                self.angle += spin_speed
                self.stunned += spin_speed
                if self.stun_anim_timer > 2:
                    self.stun_anim_timer = 0
                    self.visible = not self.visible
                else:
                    self.stun_anim_timer += 1
                self.center_y = min(self.center_y, SCREEN_HEIGHT)
                self.center_y = max(self.center_y, 0)
                self.center_x = max(self.center_x, 0)
                self.center_x = min(self.center_x, SCREEN_WIDTH)
                return
        self.frames_passed += 1
        
        if self.invincible:
            self.invincible_anim_timer += 1
            if self.invincible_anim_timer >= 6:
                self.invincible_anim_timer = 0
                self.visible = not self.visible
            if time()-self.invincible_old_time > 1.5:
                self.invincible = False
        else:
            self.visible = True
        max_speed = 9
        if self.invincible: max_speed = 3
        acceleration = 1.3
        friction = 1.3
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

        if self.engine.right_pressed and not self.engine.left_pressed:
            self.change_x += acceleration
        elif self.engine.left_pressed and not self.engine.right_pressed:
            self.change_x -= acceleration
        else:
            if self.change_x > 0: 
                self.change_x -= friction
                if self.change_x < 0:
                    self.change_x = 0
            elif self.change_x < 0:
                self.change_x += friction
                if self.change_x > 0:
                    self.change_x = 0
        self.change_x = max(min(self.change_x, max_speed), -max_speed)

        if self.change_y == 0 and not keys_pressed:
            self.angle = sin(self.frames_passed/15)*6
        else:
            self.angle = lerp(self.angle, angle_speed, 0.18)
            self.frames_passed = 0
        
        self.summon_fireball()

        collided = self.collides_with_list(self.engine.scene[DANGERS_LAYER])
        if collided and not self.invincible:
            for sprite in collided:
                if not sprite.collided:
                    self.stunned = 1
                    self.hurt_sound.play()
                    if isinstance(sprite, dangers.Rock):
                        sprite.get_hit_by_boat()
                        self.engine.score -= 1200
                    elif isinstance(sprite, dangers.Piranha):
                        self.engine.score -= 2500

        self.center_y = min(self.center_y, SCREEN_HEIGHT)
        self.center_y = max(self.center_y, 0)
        self.center_x = max(self.center_x, 0)
        self.center_x = min(self.center_x, SCREEN_WIDTH)

    def summon_fireball(self):
        self.fireball_new_time = time()
        if self.fireball_new_time-self.fireball_old_time>1.9:
            self.fireball_sound.play()
            self.fireball_old_time = self.fireball_new_time
            fireball = Fireball()
            fireball.set_position(self.center_x+75, self.center_y+40)
            self.engine.scene[PROJECTILES_LAYER].append(fireball)

    def update_animation(self, delta_time):
        self.texture = self.idle_anim.get_frame()
        self.idle_anim.update(delta_time)


class Fireball(arcade.Sprite):
    def __init__(self):
        super().__init__(scale=SCALE)
        self.scale = SCALE
        self.change_x = 20
        self.textures = [arcade.load_texture(f"src/assets/images/projectiles/fireball{i+1}.png") for i in range(2)]
        self.anim = Animation(self.textures, 0.15)
        self.collided = False

    def on_update(self, delta_time):
        self.change_x -= 0.75
        if self.left>SCREEN_WIDTH or self.right<0 or self.bottom>SCREEN_HEIGHT or self.top<0: self.kill()
        if self.change_x < 10: self.change_x = 10
        if self.alpha-20<0: self.kill(); return
        if self.collided: self.alpha -= 20
        else:
            collided = self.collides_with_list(self.engine.scene[DANGERS_LAYER])
            if collided and self.alpha == 255:
                for sprite in collided:
                    if not sprite.collided: 
                        if isinstance(sprite, dangers.Rock):
                            self.collided = True
                            sprite.get_hit_by_boat()

    def update_animation(self, delta_time):
        self.texture = self.anim.get_frame()
        self.anim.update(delta_time)