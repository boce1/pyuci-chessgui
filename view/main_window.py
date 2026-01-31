from config import *
import pygame as pg
import os
import chess
from .board_view import BoardView

class MainWindow:
    def __init__(self):
        pg.init()
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        pg.display.set_caption("Cincinnatus GUI")
        self.window = pg.display.set_mode((self.width, self.height))
        self.board_view = BoardView()

    def draw(self):
        self.window.fill(BACKGROUND_COLOR)
        self.board_view.draw(self.window)
        pg.display.update()  # Update the display

    def run(self):
        clock = pg.time.Clock()
        running = True
        ctrl = self.board_view.controller
    
        while running:
            dt = clock.tick(FPS) / 1000.0 
            mouse_pos = pg.mouse.get_pos()
    
            # 1. PROCESS ANIMATIONS
            ctrl.procces_animation_and_push_move(dt)
    
            # 2. PROCESS EVENTS (ONE LOOP ONLY)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    with ctrl.board_lock:
                        ctrl.is_force_quit_engine = True
    
                # Handle UI Buttons
                self.board_view.change_side_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.change_side_button.execute_command(event, mouse_pos)
                self.board_view.one_minutes_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.one_minutes_button.execute_command(event, mouse_pos)
                self.board_view.five_minutes_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.five_minutes_button.execute_command(event, mouse_pos)
                self.board_view.ten_minutes_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.ten_minutes_button.execute_command(event, mouse_pos)
                self.board_view.pause_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.pause_button.execute_command(event, mouse_pos)
                self.board_view.play_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.play_button.execute_command(event, mouse_pos)
    
                # Handle Board Interactions
                if ctrl.is_promoting:
                    ctrl.choose_promotion_piece(event, mouse_pos)
                else:
                    ctrl.handle_click(event, mouse_pos)
                # They are separate because promoting piece has its logic and it pushes the move
                # The animation 

            # 3. RENDER & UPDATES
            self.draw()
            ctrl.update_time()
            ctrl.engine_make_move()
    
        pg.quit()
        ctrl.shut_down_engine()