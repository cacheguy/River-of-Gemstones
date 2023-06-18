import arcade

from pyglet import clock
from pyglet.math import Vec2
from time import time
import random

import boat
import gems
from constants import *


class Game(arcade.Window):
    """Main game application."""

    def __init__(self):
        """Initialize the game"""
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, center_window=True)

        self.dt = 0
        self.fps = 0
        self.scene = None
        self.boat = None
        self.previous_gem = None

        self.score = 0
        self.level = 0
        self.enable_debug_text = True

        # Keys pressed
        self.up_pressed = False
        self.down_pressed = False
        self.right_pressed = False
        self.left_pressed = False
        self.space_pressed = False

        self.updates_per_frame = 0
        self.set_manually = False
        self.accumulator = 0

        self.set_vsync(True)
        self.set_update_rate(1/60)
        self.use_fixed_timestep = True
        self.use_interpolation = True
        self.use_snap_dt = True

        self.old_time = 0
        self.new_time = 0

    def setup(self):
        """Set up the game here. Call this method to restart the game."""
        
        arcade.Sprite.engine = self  # Allow all sprites to access this engine

        self.scene = arcade.Scene()
        for layer in ALL_LAYERS:
            self.scene.add_sprite_list(name=layer)

        self.boat = boat.Boat()
        self.boat.original_position = self.boat.position
        self.scene[BOAT_LAYER].append(self.boat)

        self.score = 0
        self.accumulator = 0
        self.background_color = (0,210,255)
        self.old_time = time()
        self.new_time = 0

    
    def on_draw(self):
        """Clear, then render the screen."""
        self.clear()
        self.scene.draw(pixelated=True)
        
        # Draw some debug text
        self.reset_debug_text()
        self.debug_text("FPS", self.fps)
        if self.enable_debug_text:
            self.debug_text("Player y", self.boat.center_y)
            self.debug_text("Player x", self.boat.center_x)
            self.debug_text("Change y", self.boat.change_y)
            self.debug_text("Change x", self.boat.change_x)
     
    def debug_text(self, item, value, round_floats=True):
        """Adds debug text to the top of the previous debug text."""
        if isinstance(value, float) and round_floats:
            text = f"{item}: {round(value, 2)}"
        else:
            text = f"{item}: {value}"
        arcade.draw_text(text=text, start_x=10, start_y=self.debug_text_y, color=arcade.csscolor.WHITE, font_size=18)
        self.debug_text_y += 30

    def reset_debug_text(self):
        """Resets the debug text's position. You should call this every frame before you call self.debug_text()"""
        self.debug_text_y = 10
      
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        match key:
            case arcade.key.UP | arcade.key.W: self.up_pressed = True
            case arcade.key.DOWN | arcade.key.S: self.down_pressed = True
            case arcade.key.LEFT | arcade.key.A: self.left_pressed = True
            case arcade.key.RIGHT | arcade.key.D: self.right_pressed = True
            case arcade.key.SPACE: self.space_pressed = True
            case arcade.key.G: self.god_mode = not self.god_mode
            case arcade.key.F: self.enable_debug_text = not self.enable_debug_text
            case arcade.key.Q: arcade.exit()
            case arcade.key.H: self.next_level()
            case arcade.key.V: self.enable_tile_stats = not self.enable_tile_stats

    def on_key_release(self, key, modifers):
        """Called when the user releases a key."""
        match key:
            case arcade.key.UP | arcade.key.W: self.up_pressed = False
            case arcade.key.DOWN | arcade.key.S: self.down_pressed = False
            case arcade.key.LEFT | arcade.key.A: self.left_pressed = False
            case arcade.key.RIGHT | arcade.key.D: self.right_pressed = False
            case arcade.key.SPACE: self.space_pressed = False

    def move_sprites(self):
        """Moves sprites based on their change_x, change_y, and change_angle attributes"""
        for spritelist in self.scene.sprite_lists:
            for sprite in spritelist:
                sprite.update()

    def on_update(self, delta_time):
        """Update all objects"""
        self.dt = delta_time
        self.fps = 1 / delta_time

        if self.use_fixed_timestep:
            if self.use_snap_dt:
                if abs(60 - abs(1/self.dt)) < 1:
                    self.dt = 1/60
                    self.set_manually = True
                else:
                    self.set_manually = False

            self.updates_per_frame = 0
            self.accumulator += self.dt
            if self.use_interpolation:
                self.boat.position = self.boat.original_position
            original_position = None

            while self.accumulator >= 1/62:
                self.updates_per_frame += 1
                original_position = self.boat.position
                self.update_everything()
                if self.accumulator < 0: self.accumulator = 0
                self.accumulator -= 1/60

            if self.use_interpolation:
                if original_position is None: original_position = self.boat.position
                alpha = self.accumulator/self.dt

                self.boat.original_position = self.boat.position
                self.boat.position = Vec2(*original_position).lerp(Vec2(*self.boat.position), alpha)

        else:
            self.updates_per_frame = 1
            self.update_everything()

        clock.tick()  # Removes unusual stuttering
        
    def update_everything(self):
        self.new_time = time()
        if self.new_time-self.old_time >= 0.5:
            gem = gems.get_random_gem()(self.previous_gem, self.new_time-self.old_time)
            self.scene[GEMS_LAYER].append(gem)
            self.old_time = time() 
            self.previous_gem = gem
            
        self.scene.on_update(delta_time=self.dt)
        self.move_sprites()
        self.scene.update_animation(delta_time=self.dt)


def main():
    """Main function to start the game."""
    window = Game()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
