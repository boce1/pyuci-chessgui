import chess
import chess.engine as engine
import os
import pygame as pg
import threading
from config import *
from view.promotion_table_view import PromotionTableView

class BoardController:
    def __init__(self):
        fen = chess.STARTING_FEN
        # fen = check_fen  # For testing purposes
        #fen =pawn_promotion_fen
        #fen = pawn_promotion_fen_black_turn
        self.board = chess.Board(fen)
        self.engine = None
        self.load_engine()
        self.white_on_bottom = True # Default orientation
        self.source_square = None
        self.legal_moves_for_source_square = []
        self.is_engine_thinking = False
        self.current_analysis = None

        self.pending_move_to_square = None
        self.is_promoting = False
        self.promotion_piece = None
        self.promotion_table = PromotionTableView()

        self.source_square_display = None
        self.target_square_display = None

        self.absent_pices_num = {
            'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0,
            'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0
        }

    def load_engine(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        engine_dir = os.path.join(current_dir, '..', 'engines')
        engine_dir = os.path.normpath(engine_dir)

        if os.name == 'nt':  # Windows
            engine_path = os.path.join(engine_dir, 'cincinnatus_windows_release.exe')
        elif os.name == 'posix':  # macOS or Linux
            engine_path = os.path.join(engine_dir, 'cincinnatus_linux_release')
        else:
            raise Exception("Unsupported OS")

        engine_path = os.path.normpath(engine_path)
        self.engine = engine.SimpleEngine.popen_uci(engine_path)
        print(f"Loaded engine from: {engine_path}")

    def is_left_mouse_button_down(self, event):
        return event.type == pg.MOUSEBUTTONDOWN and event.button == 1

    def get_square_from_mouse_pos(self, mouse_pos):
        x, y = mouse_pos
        file = (x - BOARD_X) // SQUARE_SIZE
        rank = 7 - ((y - BOARD_Y) // SQUARE_SIZE)  # Invert y-axis for chess board
        if not self.white_on_bottom:
            file = 7 - file
            rank = 7 - rank
        
        if(file < 0 or file > 7 or rank < 0 or rank > 7):
            return None

        return chess.square(file, rank)

    def choose_source_square(self, event, mouse_pos):
        if self.is_left_mouse_button_down(event):
            square = self.get_square_from_mouse_pos(mouse_pos)
            if square != None:
                self.source_square = square
                #piece = self.board.piece_at(square)
                self.get_legal_moves_for_source_square()

    def choose_target_square(self, event, mouse_pos):
        if self.is_left_mouse_button_down(event):
            square = self.get_square_from_mouse_pos(mouse_pos)
            if square != None and self.source_square != None and len(self.legal_moves_for_source_square) > 0:
                for m in self.legal_moves_for_source_square:
                    if m.to_square == square:
                        self.board.push(m)
                        self.source_square = None
                        self.get_legal_moves_for_source_square()
                        return

    def get_legal_moves_for_source_square(self):
        self.legal_moves_for_source_square = []
        if self.source_square is not None:
            all_legal_moves = list(self.board.legal_moves)
            self.legal_moves_for_source_square = [move for move in all_legal_moves if move.from_square == self.source_square]

    def is_promotion(self, move):
        piece = self.board.piece_at(move.from_square)
        if piece and piece.piece_type == chess.PAWN:
            if (piece.color == chess.WHITE and chess.square_rank(move.to_square) == 7) or \
               (piece.color == chess.BLACK and chess.square_rank(move.to_square) == 0):
                self.is_promoting = True
                return
        self.is_promoting = False
        return

    def handle_click(self, event, mouse_pos):
        # UNCOMMENT THESE LINES TO ENABLE ENGINE PLAY
        # --------------------------------------------
        if self.white_on_bottom and self.board.turn == chess.BLACK:
            return
        if self.white_on_bottom == False and self.board.turn == chess.WHITE:
            return
        
        
        if not self.is_left_mouse_button_down(event):
            return

        square = self.get_square_from_mouse_pos(mouse_pos)
        if square is None:
            return

        # STATE 1: Selecting a piece (Source)
        if self.source_square is None:
            piece = self.board.piece_at(square)
            # Only select if there's a piece and it's that color's turn
            if piece and piece.color == self.board.turn:
                self.source_square = square
                self.get_legal_moves_for_source_square()

        # STATE 2: Choosing where to move (Target)
        else:
            # DISELECTION
            if square == self.source_square:
                self.source_square = None
                self.get_legal_moves_for_source_square()
                self.is_promoting = False
                return

            # Check if the clicked square is one of the legal destinations
            move_to_make = None
            for m in self.legal_moves_for_source_square:
                if m.to_square == square:
                    move_to_make = m
                    break
            

            if move_to_make:
                self.is_promotion(move_to_make)
                if self.is_promoting:
                    self.pending_move_to_square = square # Remember the target
                    return # STOP HERE. Don't push to board yet.

                self.source_square_display = move_to_make.from_square
                self.target_square_display = move_to_make.to_square

                self.board.push(move_to_make)
                self.get_absent_pieces()

                self.source_square = None # Reset for next move
                self.legal_moves_for_source_square = []
                self.is_promoting = False
            else:
                # If user clicks a different piece of their own, change selection instead
                self.is_promoting = False
                new_piece = self.board.piece_at(square)
                if new_piece and new_piece.color == self.board.turn:
                    self.source_square = square
                    self.get_legal_moves_for_source_square()
                else:
                    # Clicked an illegal square or empty space, deselect
                    self.source_square = None
                    self.legal_moves_for_source_square = []

    def choose_promotion_piece(self, event, mouse_pos):
        if self.white_on_bottom and self.board.turn == chess.BLACK:
            return
        if self.white_on_bottom == False and self.board.turn == chess.WHITE:
            return

        if not self.is_left_mouse_button_down(event):
            return
        x, y = mouse_pos
        if x < PROMOTION_TABLE_X or x > PROMOTION_TABLE_X + PROMOTION_TABLE_WIDTH or \
            y < PROMOTION_TABLE_Y or y > PROMOTION_TABLE_Y + PROMOTION_TABLE_CELL_WIDTH:
            return
        if not self.is_promoting:
            self.promotion_piece = None
            return
        piece_index = (x - PROMOTION_TABLE_X) // PROMOTION_TABLE_CELL_WIDTH

        if piece_index == 0:
            self.promotion_piece = chess.QUEEN
        elif piece_index == 1:
            self.promotion_piece = chess.ROOK
        elif piece_index == 2:
            self.promotion_piece = chess.KNIGHT
        elif piece_index == 3:
            self.promotion_piece = chess.BISHOP

        if self.promotion_piece != None and self.pending_move_to_square:
            final_move = chess.Move(self.source_square, self.pending_move_to_square, promotion=self.promotion_piece)
            
            if final_move in self.board.legal_moves:
                self.board.push(final_move)
            
            self.source_square_display = final_move.from_square
            self.target_square_display = final_move.to_square
            
            self.promotion_piece = None
            self.pending_move_to_square = None
            self.source_square = None # Reset for next move
            self.legal_moves_for_source_square = []
            self.is_promoting = False
        
        

    def engine_make_move(self):
        # Only start the engine if its the engines turn and not already thinking
        if (self.white_on_bottom and self.board.turn == chess.BLACK or 
            not self.white_on_bottom and self.board.turn == chess.WHITE) \
            and not self.is_engine_thinking:
            if self.engine is None:
                return

            self.is_engine_thinking = True
            # Create a thread to run the calculation
            engine_thread = threading.Thread(target=self.run_engine)
            engine_thread.daemon = True  # Ensures thread dies if main program exits
            engine_thread.start()

    def run_engine(self):
        """ This runs in the background thread """
        try:
            self.is_engine_thinking = True
            # result = self.engine.play(self.board, chess.engine.Limit(
            #     white_clock=60.0, 
            #     black_clock=60.0
            # ))
            # if result.move:
            #     self.board.push(result.move)

            # 1. Start an analysis task instead of a simple "play"
            with self.engine.analysis(self.board, 
                                      chess.engine.Limit(white_clock=60.0, black_clock=60.0)) as analysis:
                self.current_analysis = analysis
                
                # 2. Wait for the engine to finish or be stopped
                for info in analysis:
                    # print(info.get("depth")) 
                    # print(info.get("score"))
                    # print(info.get("pv"))
                    # print(info.items)
                    pass

                # 3. Get the final move
                result = analysis.wait()
                if result.move:
                    self.source_square_display = result.move.from_square
                    self.target_square_display = result.move.to_square
                    self.board.push(result.move)
                    self.get_absent_pieces()

        except chess.engine.AnalysisComplete:
            pass # Analysis finished naturally
        except Exception as e:
            print(f"Engine interrupted or error: {e}")
        finally:
            self.current_analysis = None
            self.is_engine_thinking = False

    def get_absent_pieces(self):
        self.absent_pices_num = {
            'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0,
            'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0
        }
        active_piece_symbols = [p.symbol() for p in self.board.piece_map().values()]

        for p in active_piece_symbols:
            if p not in ('k', 'K'):
                self.absent_pices_num[p] += 1
        
        for p in self.absent_pices_num.keys():
            if p in ('p', 'P'):
                self.absent_pices_num[p] = 8 - self.absent_pices_num[p]
            elif p in ('N', 'n', 'B', 'b', 'R', 'r'):
                self.absent_pices_num[p] = 2 - self.absent_pices_num[p]
            elif p in ('Q', 'q'):
                self.absent_pices_num[p] = 1 - self.absent_pices_num[p]


    def change_turn(self):
        self.board.turn = not self.board.turn

    def shut_down_engine(self):
        if self.engine:
            self.engine.quit()

    