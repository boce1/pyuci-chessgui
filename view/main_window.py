from config import SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
import pygame as pg
from .board_view import BoardView
from view import board_view

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
    
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            self.draw()
        pg.quit()
        self.board_view.controller.shut_down_engine()