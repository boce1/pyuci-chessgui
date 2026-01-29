from config import *
import pygame as pg
from controller import BoardController
import os
import chess
from .promotion_table_view import PromotionTableView
from .material_score_table_view import MaterialScoreTableView
from .time_view import TimeView
from .game_status_view import GameStatusView
from .search_info_view import SearchInfoView
from .button import Button

class BoardView:
    def __init__(self):
        pg.font.init()
        
        self.controller = BoardController()

        self.pieces_images = {
            'P': None, 'N': None, 'B': None, 'R': None, 'Q': None, 'K': None,
            'p': None, 'n': None, 'b': None, 'r': None, 'q': None, 'k': None
        }
        self.load_pictures()
        self.font = pg.font.SysFont('Consolas', int(SQUARE_SIZE * 0.3), bold=True)
        self.promotion_table = PromotionTableView()
        self.material_table = MaterialScoreTableView()
        self.time_table = TimeView()
        self.status_table = GameStatusView()
        self.search_table = SearchInfoView()
        self.play_button = Button(PLAY_BUTTON_X, PLAY_BUTTON_Y, PLAY_BUTTON_WIDTH, PLAY_BUTTON_HEIGHT, self.controller.play_button_action, "Start new game", BUTTON_START)
        self.pause_button = Button(PAUSE_BUTTON_X, PAUSE_BUTTON_Y, PAUSE_BUTTON_WIDTH, PAUSE_BUTTON_HEIGHT, self.controller.stop_game, "Stop the game", BUTTON_STOP)
        self.one_minutes_button = Button(TIME_BUTTON_1_X, TIME_BUTTON_1_Y, TIME_BUTTON_1_WIDTH, TIME_BUTTON_1_HEIGHT, self.controller.set_TIME_1_MUNUTES, "1 munute")
        self.five_minutes_button = Button(TIME_BUTTON_2_X, TIME_BUTTON_2_Y, TIME_BUTTON_2_WIDTH, TIME_BUTTON_2_HEIGHT, self.controller.set_time_5_minutes, "5 munutes")
        self.ten_minutes_button = Button(TIME_BUTTON_3_X, TIME_BUTTON_3_Y, TIME_BUTTON_3_WIDTH, TIME_BUTTON_3_HEIGHT, self.controller.set_time_10_minutes, "10 munutes")
        self.change_side_button = Button(CHANGE_SIDE_BUTTON_X, CHANGE_SIDE_BUTTON_Y, CHANGE_SIDE_BUTTON_WIDTH, CHANGE_SIDE_BUTTON_HEIGHT, self.controller.change_board_orientation, "Change side")

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
        self.draw_board_background(win)
        self.draw_board(win)
        self.show_files_ranks(win)

        with self.controller.board_lock:
            self.material_table.draw(win, self.controller.absent_pices_num)
            self.draw_circle_indicating_turn(win)
            self.draw_square_in_check(win)
            self.draw_made_move(win)
            self.draw_legal_moves_for_source_square(win)

            self.time_table.draw(win, self.controller.white_clock, self.controller.black_clock)
            self.status_table.draw(win, self.controller.game_status)

        with self.controller.info_lock:   
            self.search_table.draw(win, self.controller.search_info)

        self.play_button.draw(win)
        self.pause_button.draw(win)
        self.one_minutes_button.draw(win)
        self.five_minutes_button.draw(win)
        self.ten_minutes_button.draw(win)
        self.change_side_button.draw(win)

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

            pg.draw.circle(win, HIGHLIGHT_COLOR, (center_x, center_y), SQUARE_SIZE // 2, SQUARE_SIZE // 15)

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
                rank_x = BOARD_X - rank_text.get_width() - 5
                rank_y = BOARD_Y + i * SQUARE_SIZE + SQUARE_SIZE // 2 - rank_text.get_height() // 2
            else:
                rank_x = BOARD_X - rank_text.get_width() - 5
                rank_y = BOARD_Y + (7 - i) * SQUARE_SIZE + SQUARE_SIZE // 2 - rank_text.get_height() // 2
            win.blit(rank_text, (rank_x, rank_y))

    def draw_circle_indicating_turn(self, win):
        if self.controller.board.turn == chess.WHITE:
            color = WHITE
        else:
            color = BLACK

        pg.draw.circle(win, color, (TURN_INDICATOR_X, TURN_INDICATOR_Y), TURN_INDICATOR_RADIUS)
        pg.draw.circle(win, BLACK, (TURN_INDICATOR_X, TURN_INDICATOR_Y), TURN_INDICATOR_RADIUS, 3)

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
            pg.draw.rect(win, RED, source_rect, 5)
            pg.draw.rect(win, RED, target_rect, 5)

    def draw_board_background(self, win):
        rank_char = self.font.render('a', True, FONT_COLOR) # char to get height, the all got the same height
        file_char = self.font.render('a', True, FONT_COLOR) # char to get width, the all got the same width
        margin = 5

        gap_margin = max(rank_char.get_width(), file_char.get_height())
        x = BOARD_X - gap_margin - margin
        y = BOARD_Y - gap_margin - margin
        width = BOARD_WIDTH + 2 * (gap_margin + margin)
        height = BOARD_HEIGHT + 2 * (gap_margin + margin)
        pg.draw.rect(win, WHITE, (x, y, width, height))
        #pg.draw.rect(win, BLACK, (x, y, width, height), 1)