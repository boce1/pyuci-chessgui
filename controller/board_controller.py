import chess
import chess.engine as engine
import os
import pygame as pg
import threading
import time
from config import *
from .search_info import SearchInfo
from .move_animation import MoveAnimation

class BoardController:
    def __init__(self):
        pg.mixer.init()

        fen = chess.STARTING_FEN
        # fen = check_fen  # For testing purposes
        # fen = pawn_promotion_fen
        # fen = pawn_promotion_fen_black_turn
        # fen = promotion_fen
        # fen = incufficient_material
        # fen = stalemate
        # fen = white_rook_promotion
        # fen = black_rook_promotion
        self.board = chess.Board(fen)
        self.engine = None
        self.load_engine()

        self.white_on_bottom = True # Default orientation

        self.source_square = None
        self.legal_moves_for_source_square = []

        self.is_engine_thinking = False
        self.current_analysis = None
        self.is_force_quit_engine = False

        self.is_promoting = False
        self.promotion_piece = None

        self.source_square_display = None
        self.target_square_display = None

        self.moves_to_go = MOVES_TO_GO_DEFAULT
        self.white_clock = TIME_5_MINUTES
        self.black_clock = TIME_5_MINUTES
        self.last_time = time.time()
        self.time_limit = chess.engine.Limit(white_clock=self.white_clock, black_clock=self.black_clock, remaining_moves=self.moves_to_go)
        self.last_selected_time = (self.white_clock, self.black_clock)

        self.game_status = GAME_PAUSED

        self.absent_pices_num = {
            'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0,
            'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0
        }

        self.get_absent_pieces()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        sounds_dir = os.path.join(current_dir, '..', 'sounds')
        sounds_dir = os.path.normpath(sounds_dir)
        self.move_sound = pg.mixer.Sound(os.path.join(sounds_dir, "move.mp3"))
        self.capture_sound = pg.mixer.Sound(os.path.join(sounds_dir, "capture.mp3"))
        self.generic_notification_sound = pg.mixer.Sound(os.path.join(sounds_dir, "generic_notification.mp3"))

        self.search_info = SearchInfo()

        self.board_lock = threading.Lock()
        self.info_lock = threading.Lock()

        # for pices moving animation
        self.active_animation = None
        self.secondary_animation = None  # Specifically for the Rook
        self.pending_move = None

        self.castle_map = {
            chess.G1: (chess.H1, chess.F1), # White Kingside
            chess.C1: (chess.A1, chess.D1), # White Queenside
            chess.G8: (chess.H8, chess.F8), # Black Kingside
            chess.C8: (chess.A8, chess.D8)  # Black Queenside
        }

        self.current_search_id = 0

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

    def get_square_coords(self, square):
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        if not self.white_on_bottom:
            file = 7 - file
            rank = 7 - rank
        x = BOARD_X + file * SQUARE_SIZE
        y = BOARD_Y + (7 - rank) * SQUARE_SIZE
        return x, y

    def handle_click(self, event, mouse_pos):
        if self.game_status != PLAYING:
            return
        # Block input if it's the engine's turn
        if (self.white_on_bottom and self.board.turn == chess.BLACK) or \
           (not self.white_on_bottom and self.board.turn == chess.WHITE):
            return

        # Check for mouse click
        if not self.is_left_mouse_button_down(event):
            return

        square = self.get_square_from_mouse_pos(mouse_pos)
        if square is None:
            return

        # STATE 1: Selecting a piece
        if self.source_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.source_square = square
                self.get_legal_moves_for_source_square()

        # STATE 2: Choosing target square
        else:
            # Deselect if clicking the same square
            if square == self.source_square:
                self.source_square = None
                self.legal_moves_for_source_square = []
                return

            move_to_make = next((m for m in self.legal_moves_for_source_square if m.to_square == square), None)

            if move_to_make:
                self.is_promotion(move_to_make)

                # Setup Animation
                start_px = self.get_square_coords(move_to_make.from_square)
                end_px = self.get_square_coords(move_to_make.to_square)
                piece = self.board.piece_at(move_to_make.from_square)

                self.active_animation = MoveAnimation(piece.symbol(), start_px, end_px)
                self.pending_move = move_to_make

                # 2. DETECT CASTLING: Setup Secondary Animation (The Rook)
                if self.board.is_castling(move_to_make):
                    # Determine Rook squares based on King's destination
                    # Mapping: King Dest -> (Rook From, Rook To)
                    
                    
                    r_from, r_to = self.castle_map[move_to_make.to_square]
                    r_start_px = self.get_square_coords(r_from)
                    r_end_px = self.get_square_coords(r_to)
                    r_piece = self.board.piece_at(r_from)
                    
                    if r_piece:
                        self.secondary_animation = MoveAnimation(r_piece.symbol(), r_start_px, r_end_px)

                self.legal_moves_for_source_square = []
                if self.is_promoting:
                    # Do not clear source_square yet
                    return 

                # Normal move: Clear selection immediately so animation can finish
                self.source_square = None
            else:
                # Change selection if clicking another teammate
                new_piece = self.board.piece_at(square)
                if new_piece and new_piece.color == self.board.turn:
                    self.source_square = square
                    self.get_legal_moves_for_source_square()

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

        if self.promotion_piece != None and self.pending_move:
        # Construct the REAL move with the promotion piece
            final_move = chess.Move(
                self.pending_move.from_square, 
                self.pending_move.to_square, 
                promotion=self.promotion_piece
            )

            if final_move in self.board.legal_moves:
                with self.board_lock:
                    is_capture = self.board.is_capture(final_move)
                    self.board.push(final_move)
                    self.update_game_status()
                    self.play_sound(is_capture)
                    self.get_absent_pieces()

                    self.source_square_display = final_move.from_square
                    self.target_square_display = final_move.to_square

                # Cleanup
                self.active_animation = None
                self.pending_move = None # Now we can clear it
                self.promotion_piece = None
                self.source_square = None
                self.is_promoting = False
        

    def engine_make_move(self):
        is_engine_turn = (self.white_on_bottom and self.board.turn == chess.BLACK) or \
                         (not self.white_on_bottom and self.board.turn == chess.WHITE)

        if is_engine_turn and not self.is_engine_thinking and self.game_status == PLAYING:
            if self.active_animation is not None or self.pending_move is not None:
                return

            if self.engine is None:
                return
            
            with self.board_lock:
                self.current_search_id = time.time() # Create a unique ID for this search
                search_id = self.current_search_id
                board_copy = self.board.copy()

            self.is_engine_thinking = True
            # Pass the ID into the thread
            thread = threading.Thread(target=self.run_engine, args=(board_copy, search_id))
            thread.daemon = True
            thread.start()

    def run_engine(self, board_copy, search_id):
        """ Runs in background thread with a thread-safe board snapshot """
        try:
            if not self.engine or self.is_force_quit_engine or self.game_status != PLAYING:
                return
    
            # Start analysis on the copy
            with self.engine.analysis(board_copy, self.time_limit) as analysis:
                self.current_analysis = analysis
                
                for info in analysis:
                    if self.is_force_quit_engine or self.game_status != PLAYING:
                        analysis.stop()
                        break
                    self.get_info_analysis(info)
    
                
                try:
                    result = analysis.wait()
                except (chess.engine.EngineError, chess.InvalidMoveError) as e:
                    print(f"Engine returned an invalid move or protocol error: {e}")
                    return
    
                if result.move and not self.is_force_quit_engine and self.game_status == PLAYING:
                    with self.board_lock:
                        if search_id != self.current_search_id:
                            print("Discarding move from a previous/cancelled game.")
                            return

                        # Verify move is still legal on the MAIN board
                        if result.move in self.board.legal_moves:
                            start_px = self.get_square_coords(result.move.from_square)
                            end_px = self.get_square_coords(result.move.to_square)
                            piece = self.board.piece_at(result.move.from_square)
    
                            if piece:
                                self.active_animation = MoveAnimation(piece.symbol(), start_px, end_px)
                                self.pending_move = result.move
    
                                if self.board.is_castling(result.move):
                                    r_from, r_to = self.castle_map[result.move.to_square]
                                    r_start_px = self.get_square_coords(r_from)
                                    r_end_px = self.get_square_coords(r_to)
                                    r_piece = self.board.piece_at(r_from)
                                    if r_piece:
                                        self.secondary_animation = MoveAnimation(r_piece.symbol(), r_start_px, r_end_px)
                        else:
                            print(f"Engine suggested move {result.move}, but it's no longer legal.")
    
        except (chess.engine.EngineTerminatedError, chess.engine.AnalysisComplete):
            pass # Normal engine shutdown or analysis finish
        except Exception as e:
            print(f"General Engine Thread Error: {e}")
        finally:
            self.current_analysis = None
            self.is_engine_thinking = False

    def get_info_analysis(self, info):
        with self.info_lock:
            self.search_info.update(info)


    def update_time(self):
        if self.game_status != PLAYING:
        # Crucial: Keep last_time updated so when we DO start, 
        # there isn't a huge "jump" in time.
            self.last_time = time.time()
            return
        
        # 1. Calculate how much time passed since the last update
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        # 2. Subtract from the active player
        if self.board.turn == chess.WHITE:
            self.white_clock -= delta_time
        else:
            self.black_clock -= delta_time

        # 3. Ensure clocks don't go below zero
        self.white_clock = max(0, self.white_clock)
        self.black_clock = max(0, self.black_clock)

        if self.white_clock == 0:
            self.game_status = TIME_PASSED_WHITE
            self.generic_notification_sound.play()
        if self.black_clock == 0:
            self.game_status = TIME_PASSED_BLACK
            self.generic_notification_sound.play()

    def update_game_status(self):
        if self.board.is_checkmate():
            if self.board.turn == chess.WHITE:
                self.game_status = CHECKMATE_BY_BLACK
            else:
                self.game_status = CHECKMATE_BY_WHITE
        elif self.board.is_stalemate():
            self.game_status = STALEMATE
        elif self.board.is_insufficient_material():
            self.game_status = INSUFFICIENT_MATERIAL
        elif self.white_clock == 0:
            self.game_status = TIME_PASSED_WHITE
        elif self.black_clock == 0:
            self.game_status = TIME_PASSED_BLACK

    def stop_game(self):
        with self.board_lock:
            if self.game_status == PLAYING:
                self.game_status = GAME_PAUSED

                self.source_square = None
                self.legal_moves_for_source_square = []

                self.is_engine_thinking = False
                self.current_analysis = None
                self.is_force_quit_engine = False

                self.is_promoting = False
                self.promotion_piece = None

                self.source_square_display = None
                self.target_square_display = None

                self.active_animation = None    # Clear the "ghost" pawn animation
                self.pending_move = None        # Clear the "ghost" move
                self.secondary_animation = None

                self.get_absent_pieces()

                self.board.turn = chess.WHITE

    def reset_game(self):
        with self.board_lock:
            if not self.is_engine_thinking and self.game_status != PLAYING and self.current_analysis == None:
                self.source_square = None
                self.legal_moves_for_source_square = []

                self.is_engine_thinking = False
                self.current_analysis = None
                self.is_force_quit_engine = False

                self.is_promoting = False
                self.promotion_piece = None

                self.source_square_display = None
                self.target_square_display = None

                self.search_info = SearchInfo()

                self.active_animation = None    # Clear the "ghost" pawn animation
                self.pending_move = None        # Clear the "ghost" move
                self.secondary_animation = None
                self.get_absent_pieces()

                self.board.turn = chess.WHITE

    def play_button_action(self):
        if self.game_status != PLAYING:
            self.board.set_fen(chess.STARTING_FEN)
            self.reset_game()
    
            # self.white_clock = TIME_1_MUNUTES
            # self.black_clock = TIME_1_MUNUTES
            self.white_clock, self.black_clock = self.last_selected_time
            self.last_time = time.time()
    
            self.game_status = PLAYING

    def set_TIME_1_MUNUTES(self):
        if self.game_status != PLAYING:
            self.black_clock = TIME_1_MUNUTES
            self.white_clock = TIME_1_MUNUTES
            self.last_selected_time = (self.white_clock, self.black_clock)
            self.moves_to_go = MOVES_TO_GO_BLITZ
            self.time_limit = chess.engine.Limit(white_clock=self.white_clock, black_clock=self.black_clock, remaining_moves=self.moves_to_go)

    def set_time_5_minutes(self):
        if self.game_status != PLAYING:
            self.black_clock = TIME_5_MINUTES
            self.white_clock = TIME_5_MINUTES
            self.last_selected_time = (self.white_clock, self.black_clock)
            self.moves_to_go = MOVES_TO_GO_DEFAULT
            self.time_limit = chess.engine.Limit(white_clock=self.white_clock, black_clock=self.black_clock, remaining_moves=self.moves_to_go)
        
    def set_time_10_minutes(self):
        if self.game_status != PLAYING:
            self.black_clock = TIME_10_MINUTES
            self.white_clock = TIME_10_MINUTES
            self.last_selected_time = (self.white_clock, self.black_clock)
            self.moves_to_go = MOVES_TO_GO_DEFAULT
            self.time_limit = chess.engine.Limit(white_clock=self.white_clock, black_clock=self.black_clock, remaining_moves=self.moves_to_go)

    def change_board_orientation(self):
        if self.game_status != PLAYING:
            self.white_on_bottom = not self.white_on_bottom

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

    def play_sound(self, was_capture):
        if was_capture:
            self.capture_sound.play()
        else:
            self.move_sound.play()
        
        if self.game_status in (CHECKMATE_BY_WHITE, CHECKMATE_BY_BLACK, STALEMATE, 
                                INSUFFICIENT_MATERIAL, TIME_PASSED_WHITE, TIME_PASSED_BLACK):
            self.generic_notification_sound.play()

    def play_sound_time_passed(self):
        if self.game_status in (TIME_PASSED_WHITE, TIME_PASSED_BLACK):
            self.generic_notification_sound.play()

    def procces_animation_and_push_move(self, dt):
        if self.active_animation:
            self.active_animation.update(dt)

            # Update Rook (Secondary) if it exists
            if self.secondary_animation:
                self.secondary_animation.update(dt)

            if self.active_animation.is_done:
                # Determine if we should push now or wait for Human UI
                # 1. If it's NOT a promotion, push immediately.
                # 2. If it IS an engine move (turn != human side), push immediately.
                if self.secondary_animation and not self.secondary_animation.is_done:
                    return

                is_human_turn = (self.white_on_bottom and self.board.turn == chess.WHITE) or \
                                (not self.white_on_bottom and self.board.turn == chess.BLACK)
                should_push = not self.is_promoting or not is_human_turn
                if should_push and self.pending_move:
                    with self.board_lock:
                        move = self.pending_move
                        # Finalize displays
                        self.source_square_display = move.from_square
                        self.target_square_display = move.to_square
                        is_capture = self.board.is_capture(move)
                        self.board.push(move)
                        self.update_game_status()
                        self.play_sound(is_capture)
                        self.get_absent_pieces()
                        
                        # IMPORTANT: Clear BOTH animations
                        self.active_animation = None
                        self.secondary_animation = None
                        self.pending_move = None

    def shut_down_engine(self):
        self.is_force_quit_engine = True

        # 1. Stop the current analysis first
        if self.current_analysis:
            try:
                self.current_analysis.stop()
            except:
                print("Error stoping analysis")

        # 2. Wait for the background thread to finish its loop (max 15 seconds)
        start_wait = time.time()
        while self.is_engine_thinking and (time.time() - start_wait < 15.0):
            time.sleep(0.1)

        # 3. Now safely quit the engine process
        if self.engine:
            try:
                self.engine.quit()
            except Exception as e:
                print(f"Hard closing engine: {e}")
                self.engine.close()
            finally:
                self.engine = None

    