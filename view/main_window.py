from config import *
import pygame as pg
import time
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
        self.window.fill(WHITE)  # Fill the window with white color
        self.board_view.draw(self.window)
        pg.display.update()  # Update the display

    def run(self):
        clock = pg.time.Clock()
        running = True

        while running:
            mouse_pos = pg.mouse.get_pos()
            mouse_state = pg.mouse.get_pressed()
            clock.tick(FPS) 

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    self.board_view.controller.is_force_quit_engine = True

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

                self.board_view.controller.handle_click(event, mouse_pos)
                self.board_view.controller.choose_promotion_piece(event, mouse_pos)
            
            self.draw()
            self.board_view.controller.update_time()
            self.board_view.controller.engine_make_move()
            self.board_view.controller.update_game_status()
            self.board_view.controller.reset_game()

        pg.quit()
        self.board_view.controller.shut_down_engine()