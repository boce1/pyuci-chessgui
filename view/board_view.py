from config import *
import pygame as pg
from controller import BoardController
import os
import chess
from .promotion_table_view import PromotionTableView
from .material_score_table_view import MaterialScoreTableView
from .time_view import TimeView

class BoardView:
    def __init__(self):

        self.controller = BoardController()
        self.pieces_images = {
            'P': None, 'N': None, 'B': None, 'R': None, 'Q': None, 'K': None,
            'p': None, 'n': None, 'b': None, 'r': None, 'q': None, 'k': None
        }
        self.load_pictures()
        pg.font.init()
        self.font = pg.font.SysFont('Consolas', int(SQUARE_SIZE * 0.3), bold=True)
        self.promotion_table = PromotionTableView()
        self.material_table = MaterialScoreTableView()
        self.time_table = TimeView()

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
        self.draw_legal_moves_for_source_square(win)
        self.show_files_ranks(win)
        self.material_table.draw(win, self.controller.absent_pices_num)
        self.draw_circle_indicating_turn(win)
        self.draw_square_in_check(win)
        self.draw_made_move(win)
        self.time_table.draw(win, self.controller.white_clock, self.controller.black_clock)

        self.draw_pieces(win) # need to be the last
        
        # self.controller.get_absent_pieces()

        pg.draw.rect(win, GRAY, (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT), 2)

        self.promotion_table.draw(win, self.controller.is_promoting, self.controller.board.turn)

    def draw_board(self, win):
        for rank in range(8):
            for file in range(8):
                
                # Map logical square -> screen square
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

                pg.draw.rect(win, color,(BOARD_X + col * SQUARE_SIZE, BOARD_Y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

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

            x_pos = BOARD_X + col * SQUARE_SIZE + (SQUARE_SIZE - PIECE_SIZE) // 2
            y_pos = BOARD_Y + row * SQUARE_SIZE + (SQUARE_SIZE - PIECE_SIZE) // 2

            win.blit(piece_image, (x_pos, y_pos))

    def draw_legal_moves_for_source_square(self, win):
        for move in self.controller.legal_moves_for_source_square:
            to_square = move.to_square
            rank = to_square // 8
            file = to_square % 8

            if self.controller.white_on_bottom:
                row = 7 - rank
                col = file
            else:
                row = rank
                col = 7 - file

            center_x = BOARD_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = BOARD_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2

            pg.draw.circle(win, HIGHLIGHT_COLOR, (center_x, center_y), SQUARE_SIZE * 0.3)

    def show_files_ranks(self, win):
        for i in range(8):
            file_char = chr(ord('a') + i)
            rank_char = str(8 - i)

            # Files (a-h)
            file_text = self.font.render(file_char, True, FONT_COLOR)
            if self.controller.white_on_bottom:
                file_x = BOARD_X + i * SQUARE_SIZE + SQUARE_SIZE // 2 - file_text.get_width() // 2
                file_y = BOARD_Y + BOARD_HEIGHT
            else:
                file_x = BOARD_X + (7 - i) * SQUARE_SIZE + SQUARE_SIZE // 2 - file_text.get_width() // 2
                file_y = BOARD_Y + BOARD_HEIGHT
            win.blit(file_text, (file_x, file_y))

            # Ranks (1-8)
            rank_text = self.font.render(rank_char, True, FONT_COLOR)
            if self.controller.white_on_bottom:
                rank_x = BOARD_X - rank_text.get_width()
                rank_y = BOARD_Y + i * SQUARE_SIZE + SQUARE_SIZE // 2 - rank_text.get_height() // 2
            else:
                rank_x = BOARD_X - rank_text.get_width()
                rank_y = BOARD_Y + (7 - i) * SQUARE_SIZE + SQUARE_SIZE // 2 - rank_text.get_height() // 2
            win.blit(rank_text, (rank_x, rank_y))

    def draw_circle_indicating_turn(self, win):
        if self.controller.board.turn == chess.WHITE:
            color = WHITE
        else:
            color = BLACK

        pg.draw.circle(win, color, (TURN_INDICATOR_X, TURN_INDICATOR_Y), TURN_INDICATOR_RADIUS)
        pg.draw.circle(win, BLACK, (TURN_INDICATOR_X, TURN_INDICATOR_Y), TURN_INDICATOR_RADIUS, 2)

    def draw_square_in_check(self, win):
        # Check both colors because the turn changes immediately after a move
        for color in [chess.WHITE, chess.BLACK]:
            king_square = self.controller.board.king(color)

            # is_check() is a shortcut to see if the king of the side whose turn it is is under attack
            # But board.is_attacked_by is more precise for specific highlights
            if king_square is not None:
                # We check if the king of 'color' is attacked by the opposite color
                if self.controller.board.is_attacked_by(not color, king_square):
                    rank = king_square // 8
                    file = king_square % 8

                    if self.controller.white_on_bottom:
                        row, col = 7 - rank, file
                    else:
                        row, col = rank, 7 - file

                    # Using a thicker line or a semi-transparent surface looks better
                    rect = (BOARD_X + col * SQUARE_SIZE, BOARD_Y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                    pg.draw.rect(win, HIGHLIGHT_COLOR, rect) # Explicit Red for Check

    def draw_made_move(self, win):
        if self.controller.source_square_display and self.controller.target_square_display:
            source_rank = self.controller.source_square_display // 8
            source_file = self.controller.source_square_display % 8

            target_rank = self.controller.target_square_display // 8
            target_file = self.controller.target_square_display % 8

            if self.controller.white_on_bottom:
                row_source, col_source = 7 - source_rank, source_file
                row_target, col_target = 7 - target_rank, target_file
            else:
                row_source, col_source = source_rank, 7 - source_file
                row_target, col_target = target_rank, 7 - target_file
            
            source_rect = (BOARD_X + col_source * SQUARE_SIZE, BOARD_Y + row_source * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            target_rect = (BOARD_X + col_target * SQUARE_SIZE, BOARD_Y + row_target * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pg.draw.rect(win, HIGHLIGHT_COLOR, source_rect, 5)
            pg.draw.rect(win, HIGHLIGHT_COLOR, target_rect, 5)

    def draw_time_info(self):
        pass