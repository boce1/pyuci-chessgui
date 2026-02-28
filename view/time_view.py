from config import *
import pygame as pg

class TimeView:
    def __init__(self):
        self.font = pg.font.SysFont("Consolas", int(TIME_INFO_HEIGHT * 0.4), bold=True)
        self.gap = 7
        self.collor_gap = 50
        self.white_darker_color = (max(0, WHITE_SQUARE_COLOR[0] - self.collor_gap), max(0, WHITE_SQUARE_COLOR[1] - self.collor_gap), max(0, WHITE_SQUARE_COLOR[2] - self.collor_gap))
        self.black_darker_color = (max(0, BLACK_SQUARE_COLOR[0] - self.collor_gap), max(0, BLACK_SQUARE_COLOR[1] - self.collor_gap), max(0, BLACK_SQUARE_COLOR[2] - self.collor_gap))


    def format_time(self, time):
        time = round(time)
        minutes = time // 60
        seconds = time % 60

        minutes = f"{minutes:02d}"
        seconds = f"{seconds:02d}"

        return f"{minutes}:{seconds}"

    def draw_edge_corners(self, win):
        # --- WHITE CELL ---
        x_w, y, w, h = TIME_INFO_X, TIME_INFO_Y, TIME_INFO_CELL_WIDTH, TIME_INFO_HEIGHT
        g = self.gap

        # Top-Left: Move start in (+1, +1)
        pg.draw.line(win, BLACK, (x_w + 1, y + 1), (x_w + g, y + g), 2)
        # Top-Right: Move start in (-1, +1) and end in (+1, -1)
        pg.draw.line(win, BLACK, (x_w + w - 1, y + 1), (x_w + w - g, y + g), 2)
        # Bottom-Left: Move start in (+1, -1)
        pg.draw.line(win, BLACK, (x_w + 1, y + h - 1), (x_w + g, y + h - g), 2)
        # Bottom-Right: Move start in (-1, -1)
        pg.draw.line(win, BLACK, (x_w + w - 1, y + h - 1), (x_w + w - g, y + h - g), 2)

        # --- BLACK CELL ---
        x_b = TIME_INFO_X + TIME_INFO_CELL_WIDTH

        # Top-Left
        pg.draw.line(win, BLACK, (x_b + 1, y + 1), (x_b + g, y + g), 2)
        # Top-Right
        pg.draw.line(win, BLACK, (x_b + w - 1, y + 1), (x_b + w - g, y + g), 2)
        # Bottom-Left
        pg.draw.line(win, BLACK, (x_b + 1, y + h - 1), (x_b + g, y + h - g), 2)
        # Bottom-Right
        pg.draw.line(win, BLACK, (x_b + w - 1, y + h - 1), (x_b + w - g, y + h - g), 2)

    def draw(self, win, white_clock, black_clock):
        white_time = self.font.render(self.format_time(white_clock), True, BLACK)
        black_time = self.font.render(self.format_time(black_clock), True, BLACK)

        pg.draw.rect(win, self.white_darker_color, (TIME_INFO_X, TIME_INFO_Y, TIME_INFO_CELL_WIDTH, TIME_INFO_HEIGHT)) # outer rect
        pg.draw.rect(win, WHITE_SQUARE_COLOR, 
                     (TIME_INFO_X + self.gap, TIME_INFO_Y + self.gap, TIME_INFO_CELL_WIDTH - 2 * self.gap, TIME_INFO_HEIGHT - 2 * self.gap)) # inner rect
        pg.draw.rect(win, BLACK, 
                     (TIME_INFO_X + self.gap, TIME_INFO_Y + self.gap, TIME_INFO_CELL_WIDTH - 2 * self.gap, TIME_INFO_HEIGHT - 2 * self.gap), 2) # inner rect

        pg.draw.rect(win, self.black_darker_color, (TIME_INFO_X + TIME_INFO_CELL_WIDTH, TIME_INFO_Y, TIME_INFO_CELL_WIDTH, TIME_INFO_HEIGHT)) # outer rect
        pg.draw.rect(win, BLACK_SQUARE_COLOR, 
                     (TIME_INFO_X + TIME_INFO_CELL_WIDTH + self.gap, TIME_INFO_Y + self.gap, TIME_INFO_CELL_WIDTH - 2 * self.gap, TIME_INFO_HEIGHT - 2 * self.gap)) # inner rect
        pg.draw.rect(win, BLACK, 
                     (TIME_INFO_X + TIME_INFO_CELL_WIDTH + self.gap, TIME_INFO_Y + self.gap, TIME_INFO_CELL_WIDTH - 2 * self.gap, TIME_INFO_HEIGHT - 2 * self.gap), 2) # inner rect


        win.blit(white_time, (TIME_INFO_X + TIME_INFO_CELL_WIDTH // 2 - white_time.get_width() // 2,
                               TIME_INFO_Y + TIME_INFO_HEIGHT // 2 - white_time.get_height() // 2))
        
        win.blit(black_time, (TIME_INFO_X + TIME_INFO_CELL_WIDTH + TIME_INFO_CELL_WIDTH // 2 - black_time.get_width() // 2,
                               TIME_INFO_Y + TIME_INFO_HEIGHT // 2 - black_time.get_height() // 2))

        self.draw_edge_corners(win)

        pg.draw.line(win, BLACK, (TIME_INFO_X + TIME_INFO_CELL_WIDTH, TIME_INFO_Y), (TIME_INFO_X + TIME_INFO_CELL_WIDTH, TIME_INFO_Y + TIME_INFO_HEIGHT - 1), 1)
        pg.draw.rect(win, BLACK, (TIME_INFO_X, TIME_INFO_Y, TIME_INFO_WIDTH, TIME_INFO_HEIGHT), 3)
