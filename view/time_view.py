from config import *
import pygame as pg

class TimeView:
    def __init__(self):
        self.font = pg.font.SysFont("Consolas", int(TIME_INFO_HEIGHT * 0.4), bold=True)

    def format_time(self, time):
        time = round(time)
        minutes = time // 60
        seconds = time % 60

        return f"{minutes}:{seconds}"

    def draw(self, win, white_clock, black_clock):
        white_time = self.font.render(self.format_time(white_clock), True, BLACK)
        black_time = self.font.render(self.format_time(black_clock), True, BLACK)

        pg.draw.rect(win, BLACK, (TIME_INFO_X, TIME_INFO_Y, TIME_INFO_WIDTH, TIME_INFO_HEIGHT), 5)
        win.blit(white_time, (TIME_INFO_X + TIME_INFO_CELL_WIDTH // 2 - white_time.get_width() // 2,
                               TIME_INFO_Y + TIME_INFO_HEIGHT // 2 - white_time.get_height() // 2))
        
        win.blit(black_time, (TIME_INFO_X + TIME_INFO_CELL_WIDTH + TIME_INFO_CELL_WIDTH // 2 - black_time.get_width() // 2,
                               TIME_INFO_Y + TIME_INFO_HEIGHT // 2 - white_time.get_height() // 2))

        pg.draw.line(win, BLACK, (TIME_INFO_X + TIME_INFO_CELL_WIDTH, TIME_INFO_Y), (TIME_INFO_X + TIME_INFO_CELL_WIDTH, TIME_INFO_Y + TIME_INFO_HEIGHT - 1), 3)
