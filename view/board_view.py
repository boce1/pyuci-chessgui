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
        
        # UI Elements
        self.promotion_table = PromotionTableView()
        self.material_table = MaterialScoreTableView()
        self.time_table = TimeView()
        self.status_table = GameStatusView()
        self.search_table = SearchInfoView()
        
        # Buttons
        self.play_button = Button(PLAY_BUTTON_X, PLAY_BUTTON_Y, PLAY_BUTTON_WIDTH, PLAY_BUTTON_HEIGHT, self.controller.play_game, "Start new game", BUTTON_START)
        self.pause_button = Button(PAUSE_BUTTON_X, PAUSE_BUTTON_Y, PAUSE_BUTTON_WIDTH, PAUSE_BUTTON_HEIGHT, self.controller.stop_game, "Stop the game", BUTTON_STOP)
        self.one_minutes_button = Button(TIME_BUTTON_1_X, TIME_BUTTON_1_Y, TIME_BUTTON_1_WIDTH, TIME_BUTTON_1_HEIGHT, self.controller.set_time_1_minute, "1 minute")
        self.five_minutes_button = Button(TIME_BUTTON_2_X, TIME_BUTTON_2_Y, TIME_BUTTON_2_WIDTH, TIME_BUTTON_2_HEIGHT, self.controller.set_time_5_minutes, "5 minutes")
        self.ten_minutes_button = Button(TIME_BUTTON_3_X, TIME_BUTTON_3_Y, TIME_BUTTON_3_WIDTH, TIME_BUTTON_3_HEIGHT, self.controller.set_time_10_minutes, "10 minutes")
        self.change_side_button = Button(CHANGE_SIDE_BUTTON_X, CHANGE_SIDE_BUTTON_Y, CHANGE_SIDE_BUTTON_WIDTH, CHANGE_SIDE_BUTTON_HEIGHT, self.controller.change_board_orientation, "Change side")

    def load_pictures(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pics_dir = os.path.normpath(os.path.join(current_dir, '..', 'pics'))
        
        mapping = {
            'P': "white-pawn.png", 'N': "white-knight.png", 'B': "white-bishop.png",
            'R': "white-rook.png", 'Q': "white-queen.png", 'K': "white-king.png",
            'p': "black-pawn.png", 'n': "black-knight.png", 'b': "black-bishop.png",
            'r': "black-rook.png", 'q': "black-queen.png", 'k': "black-king.png"
        }
        
        for symbol, filename in mapping.items():
            path = os.path.join(pics_dir, filename)
            self.pieces_images[symbol] = pg.transform.scale(pg.image.load(path), (PIECE_SIZE, PIECE_SIZE)).convert_alpha() # type: ignore

    def draw(self, win):
        # 1. Background and Board Structure
        self.draw_board_background(win)
        self.draw_board(win)
        self.show_files_ranks(win)

        with self.controller.board_lock:
            # 2. Highlights and Visual Indicators
            self.draw_square_in_check(win)
            self.draw_made_move(win)
            self.draw_legal_moves_for_source_square(win)

            # 3. Draw Pieces
            self.draw_pieces_with_animation(win)

            # 4. Tables and Info
            self.material_table.draw(win, self.controller.absent_pices_num)
            self.draw_circle_indicating_turn(win)
            self.time_table.draw(win, self.controller.white_clock, self.controller.black_clock)
            self.status_table.draw(win, self.controller.game_status) 
            self.search_table.draw(win, self.controller.search_info)

        # 5. UI Buttons
        self.play_button.draw(win)
        self.pause_button.draw(win)
        self.one_minutes_button.draw(win)
        self.five_minutes_button.draw(win)
        self.ten_minutes_button.draw(win)
        self.change_side_button.draw(win)

        # 6. Overlays (Promotion needs to be on top of everything)
        pg.draw.rect(win, GRAY, (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT), 2)
        self.promotion_table.draw(win, self.controller.is_promoting, self.controller.board.turn)

    def draw_board(self, win):
        for rank in range(8):
            for file in range(8):
                if self.controller.white_on_bottom:
                    row, col = 7 - rank, file
                else:
                    row, col = rank, 7 - file

                color = WHITE_SQUARE_COLOR if (rank + file) % 2 == 1 else BLACK_SQUARE_COLOR
                pg.draw.rect(win, color, (BOARD_X + col * SQUARE_SIZE, BOARD_Y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces_with_animation(self, win):
        """Combined method to handle static pieces, the primary piece, and secondary pieces (like Rooks in castling)."""
        hidden_squares = []
        
        # 1. Identify which squares are 'empty' because pieces are moving
        if self.controller.pending_move:
            # Hide the primary piece (usually the King in castling)
            hidden_squares.append(self.controller.pending_move.from_square)
            
            # If it's a castle, we also need to hide the Rook's starting square
            if self.controller.board.is_castling(self.controller.pending_move):
                # Map King's destination to the Rook's original position
                rook_start_sq = self.controller.castle_map.get(self.controller.pending_move.to_square)
                if rook_start_sq is not None:
                    hidden_squares.append(rook_start_sq)

        # 2. Draw all static pieces
        for square, piece in self.controller.board.piece_map().items():
            if square in hidden_squares:
                continue  # Don't draw pieces currently in motion
            
            piece_image = self.pieces_images.get(piece.symbol())
            if piece_image:
                x, y = self.controller.get_square_coords(square)
                offset = (SQUARE_SIZE - PIECE_SIZE) // 2
                win.blit(piece_image, (x + offset, y + offset))

        # 3. Draw the primary animating piece (King)
        if self.controller.active_animation:
            self._draw_anim_helper(win, self.controller.active_animation)

        # 4. Draw the secondary animating piece (Rook)
        if self.controller.secondary_animation:
            self._draw_anim_helper(win, self.controller.secondary_animation)


    def _draw_anim_helper(self, win, anim):
        """Helper to render a single animation object."""
        anim_img = self.pieces_images.get(anim.piece_symbol)
        if anim_img:
            offset = (SQUARE_SIZE - PIECE_SIZE) // 2
            win.blit(anim_img, (anim.current_pos.x + offset, anim.current_pos.y + offset))


    def draw_legal_moves_for_source_square(self, win):
        for move in self.controller.legal_moves_for_source_square:
            to_square = move.to_square
            rank, file = to_square // 8, to_square % 8
            row, col = (7 - rank, file) if self.controller.white_on_bottom else (rank, 7 - file)
            center = (BOARD_X + col * SQUARE_SIZE + SQUARE_SIZE // 2, BOARD_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2)
            pg.draw.circle(win, HIGHLIGHT_COLOR, center, SQUARE_SIZE // 2, SQUARE_SIZE // 15)

    def show_files_ranks(self, win):
        for i in range(8):
            file_char, rank_char = chr(ord('a') + i), str(8 - i)
            f_text = self.font.render(file_char, True, FONT_COLOR)
            r_text = self.font.render(rank_char, True, FONT_COLOR)
            
            idx = i if self.controller.white_on_bottom else (7 - i)
            win.blit(f_text, (BOARD_X + idx * SQUARE_SIZE + SQUARE_SIZE // 2 - f_text.get_width() // 2, BOARD_Y + BOARD_HEIGHT))
            
            idy = i if self.controller.white_on_bottom else (7 - i)
            win.blit(r_text, (BOARD_X - r_text.get_width() - 5, BOARD_Y + idy * SQUARE_SIZE + SQUARE_SIZE // 2 - r_text.get_height() // 2))

    def draw_circle_indicating_turn(self, win):
        color = WHITE if self.controller.board.turn == chess.WHITE else BLACK
        pg.draw.circle(win, color, (TURN_INDICATOR_X, TURN_INDICATOR_Y), TURN_INDICATOR_RADIUS)
        pg.draw.circle(win, BLACK, (TURN_INDICATOR_X, TURN_INDICATOR_Y), TURN_INDICATOR_RADIUS, 3)

    def draw_square_in_check(self, win):
        for color in [chess.WHITE, chess.BLACK]:
            king_square = self.controller.board.king(color)
            if king_square is not None and self.controller.board.is_attacked_by(not color, king_square):
                rank, file = king_square // 8, king_square % 8
                row, col = (7 - rank, file) if self.controller.white_on_bottom else (rank, 7 - file)
                rect = (BOARD_X + col * SQUARE_SIZE, BOARD_Y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pg.draw.rect(win, HIGHLIGHT_COLOR, rect)

    def draw_made_move(self, win):
        if self.controller.source_square_display and self.controller.target_square_display:
            for sq in [self.controller.source_square_display, self.controller.target_square_display]:
                rank, file = sq // 8, sq % 8
                row, col = (7 - rank, file) if self.controller.white_on_bottom else (rank, 7 - file)
                pg.draw.rect(win, RED, (BOARD_X + col * SQUARE_SIZE, BOARD_Y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)

    def draw_board_background(self, win):
        margin = 20
        rect = (BOARD_X - margin, BOARD_Y - margin, BOARD_WIDTH + 2*margin, BOARD_HEIGHT + 2*margin)
        pg.draw.rect(win, WHITE, rect)