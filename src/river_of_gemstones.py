import arcade
from tkinter import simpledialog

from pyglet import clock
from pyglet.math import Vec2
from time import time
import random
import json

import boat
import gems
import dangers
from constants import *

import os
from pathlib import Path
import sys
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.chdir(Path(os.path.dirname(__file__)))
else:
    os.chdir(Path(os.path.dirname(__file__)).parents[0])


class Game(arcade.Window):
    """Main game application."""

    def __init__(self):
        """Initialize the game"""
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, center_window=True)
        self.dt = 0
        self.main_music = arcade.play_sound(arcade.Sound("src/assets/sounds/music.mp3", streaming=True), looping=True)
        self.state = "start"

    def setup(self):
        """Set up the game here. Call this method to restart the game."""
        self.fps = 0

        self.score = 0

        # Keys pressed
        self.up_pressed = False
        self.down_pressed = False
        self.right_pressed = False
        self.left_pressed = False

        self.updates_per_frame = 0
        self.set_manually = False
        self.accumulator = 0

        self.set_vsync(True)
        self.set_update_rate(1/60)
        self.use_fixed_timestep = True
        self.use_interpolation = True
        self.use_snap_dt = True

        self.time_text = arcade.Text(text="", start_x=10, start_y=SCREEN_HEIGHT-48, 
                                      font_name="Kenney Pixel", font_size=60)
        self.score_text = arcade.Text(text="", start_x=10, start_y=SCREEN_HEIGHT-110, 
                                      font_name="Kenney Pixel", font_size=60)

        self.bg_distance = 0
        
        self.high_score_texts = []
        
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

        self.piranha_count = 0

        background_path = "src/assets/images/background.png"
        main_background = arcade.Sprite(filename=background_path, scale=SCALE)
        main_background.left = 0
        main_background.bottom = 0
        self.scene[BACKGROUNDS_LAYER].append(main_background)
        i = 1
        while True:
            background = arcade.Sprite(filename=background_path, scale=SCALE)
            background.left = main_background.width*i
            if background.left > SCREEN_WIDTH+main_background.width: break
            background.bottom = 0
            self.scene[BACKGROUNDS_LAYER].append(background)
            i+=1

        additional_backgrounds = []
        for bottom_background in self.scene[BACKGROUNDS_LAYER]:
            i = 1
            while True:
                background = arcade.Sprite(filename=background_path, scale=SCALE)
                background.bottom = bottom_background.height*i
                if background.bottom > SCREEN_HEIGHT: break
                background.center_x = bottom_background.center_x
                additional_backgrounds.append(background)
                i+=1
        for sprite in additional_backgrounds: self.scene[BACKGROUNDS_LAYER].append(sprite)
        self.mouse_pressed = False
        self.play_again_button = None
        self.guis = []
        self.topleft_box = arcade.SpriteSolidColor(370, 126, (0,0,20,180))
        self.topleft_box.left = 0; self.topleft_box.top = SCREEN_HEIGHT
        self.start_text = arcade.Text(text="Press any key to start", start_x=SCREEN_WIDTH/2, start_y=SCREEN_HEIGHT/2, 
                                      anchor_x="center", 
                                      anchor_y="center", font_name="Kenney Pixel", font_size=60)
        self.start_box = arcade.SpriteSolidColor(self.start_text.content_width+50, self.start_text.content_height+30, 
                                                 (0,0,20,180))
        self.start_box.set_position(SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
        self.show_fps = False

    def set_times(self):
        self.gem_old_time = time()
        self.gem_new_time = 0

        self.rock_old_time = time()
        self.rock_new_time = random.randint(0,100)/100

        self.piranha_old_time = time()
        self.piranha_new_time = random.randint(0,100)/100
        self.start_time = time()
        
    def on_draw(self):
        """Clear, then render the screen."""
        self.clear()
        self.scene.draw(pixelated=True)
        
        # Draw some debug text
        self.reset_debug_text()
        if self.show_fps: self.debug_text("FPS", self.fps)
        # self.debug_text("Time Elapsed", time()-self.start_time)
        if self.state == "start":
            self.start_box.draw()
            self.start_text.draw()
        if self.state == "game":
            self.topleft_box.draw()
            self.time_text.text = f"Time: {round(60-(time()-self.start_time), 2)}"
            self.time_text.draw()
            self.score_text.text = f"Score: {self.score}"
            self.score_text.draw()
        for gui in self.guis:
            gui.draw()
     
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
            case arcade.key.F: self.show_fps = not self.show_fps
        if self.state == "start": self.state = "game"; self.set_times()

    def on_key_release(self, key, modifers):
        """Called when the user releases a key."""
        match key:
            case arcade.key.UP | arcade.key.W: self.up_pressed = False
            case arcade.key.DOWN | arcade.key.S: self.down_pressed = False
            case arcade.key.LEFT | arcade.key.A: self.left_pressed = False
            case arcade.key.RIGHT | arcade.key.D: self.right_pressed = False
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
                if self.state == "game":
                    self.update_game()
                elif self.state == "high_score":
                    self.update_high_score()
                if self.accumulator < 0: self.accumulator = 0
                self.accumulator -= 1/60

            if self.use_interpolation:
                if original_position is None: original_position = self.boat.position
                alpha = self.accumulator/self.dt

                self.boat.original_position = self.boat.position
                self.boat.position = Vec2(*original_position).lerp(Vec2(*self.boat.position), alpha)

        else:
            self.updates_per_frame = 1
            if self.state == "game":
                self.update_game()
            elif self.state == "high_score":
                self.update_high_score()

        clock.tick()  # Removes unusual stuttering
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT: self.mouse_pressed = True
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT: self.mouse_pressed = False
    
    def update_game(self):
        if time()-self.start_time>=60:
            self.state = "high_score"
            name = simpledialog.askstring(title="Game complete!", prompt="Enter name\t\t\t\t")
            with open("src/assets/high_scores.json") as f:
                high_scores: dict = json.load(f)
            if not name: name = "PLAYER"
            name = name.strip()
            name = name.upper()
            while True:
                if high_scores.get(name): name += " "
                else: break
            high_scores[name] = self.score
            high_scores = dict(sorted(high_scores.items(), key=lambda x:x[1], reverse=True))
            widths = []
            gui_texts = []
            text = arcade.Text(text=f"TOP 10 LEADERBOARD", 
                                start_x=SCREEN_WIDTH/2, start_y=SCREEN_HEIGHT-80, 
                                anchor_x="center", font_name="Kenney Pixel", font_size=65)
            gui_texts.append(text)
            widths.append(text.content_width)
            i = 0
            for key, value in high_scores.copy().items():
                if not i >= 10:
                    if name == key: color = (50, 164, 49)
                    else: color = arcade.color.WHITE
                    text = arcade.Text(text=f"{key.rstrip()}: {value}", 
                                        start_x=SCREEN_WIDTH/2, start_y=SCREEN_HEIGHT-(160)-i*50, 
                                        anchor_x="center", font_name="Kenney Pixel", font_size=65, color=color)
                    gui_texts.append(text)
                    widths.append(text.content_width)
                else:
                    del high_scores[key]
                i += 1

            text = arcade.Text(text=f"YOUR SCORE: {self.score}", 
                               start_x=SCREEN_WIDTH/2, start_y=SCREEN_HEIGHT-700, 
                               anchor_x="center", font_name="Kenney Pixel", font_size=65, color=(50, 164, 49))
            gui_texts.append(text)
            widths.append(text.content_width)

            with open("src/assets/high_scores.json", "w") as f:
                json.dump(high_scores, f)
            high_scores_box = arcade.SpriteSolidColor(width=max(widths)+50, height=SCREEN_HEIGHT-30, 
                                                      color=(0,0,20,180))
            high_scores_box.set_position(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            self.guis.append(high_scores_box)

            self.play_again_button = arcade.SpriteSolidColor(width=452, height=92, color=(50, 164, 49))
            self.play_again_button.set_position(SCREEN_WIDTH/2, 100)
            self.guis.append(self.play_again_button)

            text = arcade.Text(text=f"PLAY AGAIN", 
                               start_x=SCREEN_WIDTH/2, start_y=100, 
                               anchor_x="center", anchor_y="center", font_name="Kenney Pixel", font_size=65)
            self.guis.append(text)

            for text in gui_texts:
                self.guis.append(text)
        self.gem_new_time = time()
        self.rock_new_time = time()
        self.piranha_new_time = time()
        if self.gem_new_time-self.gem_old_time >= 0.7:
            gem = gems.get_random_gem()()
            self.scene[GEMS_LAYER].append(gem)
            self.gem_old_time = time() 

        if self.rock_new_time-self.rock_old_time >= 1.5:
            rock = dangers.Rock()
            self.scene[DANGERS_LAYER].append(rock)
            self.rock_old_time = time() 

        if self.piranha_new_time-self.piranha_old_time >= 3:
            piranha = dangers.Piranha()
            self.piranha_count += 1
            count = random.choice([0,0,1,1,2])
            if self.piranha_count > random.randint(7,10):
                piranha.scale=SCALE*2
                piranha.color=(0,255,255)
                piranha.change_x = -20
                self.piranha_count = 0
                count = 4
            for i in range(count):
                piranha2 = dangers.Piranha()
                piranha2.center_y = random.randint(piranha2.height, SCREEN_HEIGHT-piranha2.height)
                if i == 0 and random.choice((True, False, False)) and not count == 4:
                    piranha2.color = (255,255,0)
                    if piranha2.center_y > SCREEN_HEIGHT/2: piranha2.change_y = -1.2
                    else: piranha2.change_y = 1.2
                self.scene[DANGERS_LAYER].append(piranha2)
            self.scene[DANGERS_LAYER].append(piranha)
            self.piranha_old_time = time() 

        if self.scene[BACKGROUNDS_LAYER][0].right<0:
            self.scene[BACKGROUNDS_LAYER].move(self.scene[BACKGROUNDS_LAYER][0].width, 0)
        self.scene[BACKGROUNDS_LAYER].move(-3, 0)
        
        self.scene.on_update(delta_time=self.dt)
        self.move_sprites()
        self.scene.update_animation(delta_time=self.dt)
        self.score = round(self.score)
        if self.score<0: self.score=0

    def update_high_score(self):
        if self.play_again_button.collides_with_point([self._mouse_x, self._mouse_y]):
            self.play_again_button.color = (50*1.5, 164*1.5, 49*1.5)
            if self.mouse_pressed:
                self.state = "game"
                self.setup()
                self.set_times()
        else:
            self.play_again_button.color = (50, 164, 49)


def main():
    """Main function to start the game."""
    window = Game()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
