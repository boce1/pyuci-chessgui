from config import *
import pygame as pg
from .board_view import BoardView

class MainWindow:
    def __init__(self):
        pg.init()
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
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

            clock.tick(FPS) 
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                #self.board_view.controller.choose_source_square(event, mouse_pos)
                #self.board_view.controller.choose_target_square(event, mouse_pos)
                self.board_view.controller.handle_click(event, mouse_pos)
            self.draw()
            self.board_view.controller.engine_make_move()
        pg.quit()
        self.board_view.controller.shut_down_engine()