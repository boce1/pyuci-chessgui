from config import *
import pygame as pg
from controller import BoardController
import os

class BoardView:
    def __init__(self):
        self.x = (SCREEN_WIDTH - BOARD_WIDTH) // 2 
        self.y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2
        self.controller = BoardController()
        self.pieces_images = {
            'P': None, 'N': None, 'B': None, 'R': None, 'Q': None, 'K': None,
            'p': None, 'n': None, 'b': None, 'r': None, 'q': None, 'k': None
        }
        self.load_pictures()
        pg.font.init()
        self.font = pg.font.SysFont('Consolas', int(SQUARE_SIZE * 0.3), bold=True)
        self.white_on_bottom = True  # Default orientation

    def load_pictures(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pics_dir = os.path.join(current_dir, '..', 'pics')
        pics_dir = os.path.normpath(pics_dir)

        self.pieces_images['P'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-pawn.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['N'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-knight.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['B'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-bishop.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['R'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-rook.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['Q'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-queen.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['K'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-king.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['p'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-pawn.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['n'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-knight.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['b'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-bishop.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['r'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-rook.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['q'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-queen.png")), (PIECE_SIZE, PIECE_SIZE))
        self.pieces_images['k'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-king.png")), (PIECE_SIZE, PIECE_SIZE))

    def draw(self, win):
        # Placeholder for drawing the chess board
        self.draw_board(win)
        self.draw_pieces(win)
        self.show_files_ranks(win)
        pg.draw.rect(win, GRAY, (self.x, self.y, BOARD_WIDTH, BOARD_HEIGHT), 3)

    def draw_board(self, win):
        for rank in range(8):
            for file in range(8):
                
                # Map logical square → screen square
                if self.controller.white_on_bottom:
                    row = 7 - rank
                    col = file
                else:
                    row = rank
                    col = 7 - file

                # Square color (DO NOT flip this)
                if (rank + file) % 2 == 1:
                    color = WHITE_SQUARE_COLOR
                else:
                    color = BLACK_SQUARE_COLOR

                pg.draw.rect(win, color,(self.x + col * SQUARE_SIZE, self.y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self, win):
        for square, piece in self.controller.board.piece_map().items():
            piece_symbol = piece.symbol()
            piece_image = self.pieces_images.get(piece_symbol)
            if not piece_image:
                continue

            rank = square // 8
            file = square % 8

            if self.controller.white_on_bottom:
                row = 7 - rank
                col = file
            else:
                row = rank
                col = 7 - file

            x_pos = self.x + col * SQUARE_SIZE + (SQUARE_SIZE - PIECE_SIZE) // 2
            y_pos = self.y + row * SQUARE_SIZE + (SQUARE_SIZE - PIECE_SIZE) // 2

            win.blit(piece_image, (x_pos, y_pos))

    def show_files_ranks(self, win):
        for i in range(8):
            file_char = chr(ord('a') + i)
            rank_char = str(8 - i)

            # Files (a-h)
            file_text = self.font.render(file_char, True, FONT_COLOR)
            if self.controller.white_on_bottom:
                file_x = self.x + i * SQUARE_SIZE + SQUARE_SIZE // 2 - file_text.get_width() // 2
                file_y = self.y + BOARD_HEIGHT
            else:
                file_x = self.x + (7 - i) * SQUARE_SIZE + SQUARE_SIZE // 2 - file_text.get_width() // 2
                file_y = self.y + BOARD_HEIGHT
            win.blit(file_text, (file_x, file_y))

            # Ranks (1-8)
            rank_text = self.font.render(rank_char, True, FONT_COLOR)
            if self.controller.white_on_bottom:
                rank_x = self.x - rank_text.get_width()
                rank_y = self.y + i * SQUARE_SIZE + SQUARE_SIZE // 2 - rank_text.get_height() // 2
            else:
                rank_x = self.x - rank_text.get_width()
                rank_y = self.y + (7 - i) * SQUARE_SIZE + SQUARE_SIZE // 2 - rank_text.get_height() // 2
            win.blit(rank_text, (rank_x, rank_y))
        