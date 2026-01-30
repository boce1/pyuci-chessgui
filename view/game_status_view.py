from config import *
import pygame as pg

class GameStatusView:
    def __init__(self):
        self.font = pg.font.SysFont('Consolas', int(GAME_STATUS_HEIGHT * 0.8), bold=False)
        self.paused_message = self.font.render("Choose time and side", True, BLACK)
        self.playing_message = self.font.render("Game Analysis", True, BLACK)
        self.lose_on_time_white = self.font.render("White lost on time", True, BLACK)
        self.lose_on_time_black = self.font.render("Black lost on time", True, BLACK)
        self.draw_insufficient_material = self.font.render("Draw by Incufficient material", True, BLACK)
        self.draw_stalemate = self.font.render("Draw by Stalemate", True, BLACK)
        self.checkmate_white = self.font.render("White won. Checkmate", True, BLACK)
        self.checkmate_black = self.font.render("Black won. Checkmate", True, BLACK)
        self.message = None

    def draw(self, win, game_status):
        if game_status == PLAYING:
            self.message = self.playing_message
        elif game_status == GAME_PAUSED:
            self.message = self.paused_message
        elif game_status == CHECKMATE_BY_WHITE:
            self.message = self.checkmate_white
        elif game_status == CHECKMATE_BY_BLACK:
            self.message = self.checkmate_black
        elif game_status == TIME_PASSED_WHITE:
            self.message = self.lose_on_time_white
        elif game_status == TIME_PASSED_BLACK:
            self.message = self.lose_on_time_black
        elif game_status == INSUFFICIENT_MATERIAL:
            self.message = self.draw_insufficient_material
        elif game_status == STALEMATE:
            self.message = self.draw_stalemate

        # pg.draw.rect(win, BLACK, (GAME_STATUS_X, GAME_STATUS_Y, GAME_STATUS_WIDTH, GAME_STATUS_HEIGHT), 1)
        win.blit(self.message, (GAME_STATUS_X + GAME_STATUS_WIDTH // 2 - self.message.get_width() // 2,
                                GAME_STATUS_Y + GAME_STATUS_HEIGHT // 2 - self.message.get_height() // 2))
