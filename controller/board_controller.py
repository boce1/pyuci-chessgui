import chess
import chess.engine as engine
import os
import pygame as pg
import threading
import time
import sys
from config import *
from .search_info import SearchInfo
from .move_animation import MoveAnimation
from .file_path import get_resource_path

class BoardController:
    def __init__(self):
        pg.mixer.init()

        fen = chess.STARTING_FEN
        # fen = check_fen  # For testing purposes
        # fen = pawn_promotion_fen
        # fen = pawn_promotion_fen_black_turn
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

        self.move_sound = pg.mixer.Sound(get_resource_path(os.path.join("sounds", "move.mp3")))
        self.capture_sound = pg.mixer.Sound(get_resource_path(os.path.join("sounds", "capture.mp3")))
        self.generic_notification_sound = pg.mixer.Sound(get_resource_path(os.path.join("sounds", "generic_notification.mp3")))

        self.search_info = SearchInfo()

        self.board_lock = threading.Lock()

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
        # Choose the filename based on the OS
        if os.name == 'nt':  # Windows (or Wine)
            engine_file = 'cincinnatus_windows_release.exe'
        else:  # Linux / MacOS
            engine_file = 'cincinnatus_linux_release'

        # Use your helper function to find the exact path
        # We join 'engines' and the filename
        relative_engine_path = os.path.join('engines', engine_file)
        engine_path = get_resource_path(relative_engine_path)

        # Double-check the file exists to prevent a silent crash
        if not os.path.exists(engine_path):
            raise FileNotFoundError(f"Engine not found at: {engine_path}")

        # 4. Start the engine
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
        # 1. Thread-Safe State Check
        # We lock here to check if the game is active and if it's the human's turn.
        with self.board_lock:
            if self.game_status != PLAYING:
                return

            # Determine if it is the human's turn to move
            is_human_turn = (self.white_on_bottom and self.board.turn == chess.WHITE) or \
                            (not self.white_on_bottom and self.board.turn == chess.BLACK)

            if not is_human_turn:
                return

            # Peek at the board state while still inside the lock
            square = self.get_square_from_mouse_pos(mouse_pos)
            if square is None:
                return

            piece_at_square = self.board.piece_at(square)
            current_turn = self.board.turn

        # 2. UI Event Check (Lock not needed for local event processing)
        if not self.is_left_mouse_button_down(event):
            return

        # 3. State Machine Logic
        if self.source_square is None:
            # Selecting a piece
            if piece_at_square and piece_at_square.color == current_turn:
                self.source_square = square
                # This generates moves based on the current board state
                self.get_legal_moves_for_source_square()

        else:
            # Choosing a target square
            if square == self.source_square:
                self.source_square = None
                self.legal_moves_for_source_square = []
                return

            # Find if the clicked square is a legal destination
            move_to_make = next((m for m in self.legal_moves_for_source_square if m.to_square == square), None)

            if move_to_make:
                # Check for promotion (UI logic)
                self.is_promotion(move_to_make)

                # 4. Critical Section: Updating shared animation and pending move
                with self.board_lock:
                    # Re-verify turn hasn't changed while we were processing the click
                    if self.board.turn != current_turn:
                        return

                    start_px = self.get_square_coords(move_to_make.from_square)
                    end_px = self.get_square_coords(move_to_make.to_square)
                    piece = self.board.piece_at(move_to_make.from_square)

                    if piece:
                        self.active_animation = MoveAnimation(piece.symbol(), start_px, end_px)
                        self.pending_move = move_to_make

                        # Castling logic: Setup the Rook animation
                        if self.board.is_castling(move_to_make):
                            r_from, r_to = self.castle_map[move_to_make.to_square]
                            r_start_px = self.get_square_coords(r_from)
                            r_end_px = self.get_square_coords(r_to)
                            r_piece = self.board.piece_at(r_from)
                            if r_piece:
                                self.secondary_animation = MoveAnimation(r_piece.symbol(), r_start_px, r_end_px)

                self.legal_moves_for_source_square = []
                if not self.is_promoting:
                    self.source_square = None
            else:
                # Change selection if clicking a different piece of the same color
                if piece_at_square and piece_at_square.color == current_turn:
                    self.source_square = square
                    self.get_legal_moves_for_source_square()

    def choose_promotion_piece(self, event, mouse_pos):
        # 1. Early Exit for Input (No lock needed for mouse button check)
        if not self.is_left_mouse_button_down(event):
            return

        # 2. Coordinate Check (UI only)
        x, y = mouse_pos
        if not (PROMOTION_TABLE_X <= x <= PROMOTION_TABLE_X + PROMOTION_TABLE_WIDTH and
                PROMOTION_TABLE_Y <= y <= PROMOTION_TABLE_Y + PROMOTION_TABLE_CELL_WIDTH):
            return

        # 3. Critical State Check
        with self.board_lock:
            # Check if it's actually the human's turn
            is_human_turn = (self.white_on_bottom and self.board.turn == chess.WHITE) or \
                            (not self.white_on_bottom and self.board.turn == chess.BLACK)

            if not is_human_turn or not self.is_promoting or self.game_status != PLAYING:
                return

            # Map click to piece
            piece_index = int((x - PROMOTION_TABLE_X) // PROMOTION_TABLE_CELL_WIDTH)
            promo_pieces = [chess.QUEEN, chess.ROOK, chess.KNIGHT, chess.BISHOP]

            if 0 <= piece_index < len(promo_pieces):
                selected_piece = promo_pieces[piece_index]
            else:
                return

            if self.pending_move:
                # Construct the move with the chosen piece
                final_move = chess.Move(
                    self.pending_move.from_square, 
                    self.pending_move.to_square, 
                    promotion=selected_piece
                )

                # 4. Finalize Move (Already inside the lock)
                if final_move in self.board.legal_moves:
                    is_capture = self.board.is_capture(final_move)
                    self.board.push(final_move)

                    # Update status (Checkmate/Stalemate/Time)
                    self.update_game_status()

                    # Visual/Sound updates
                    self.play_sound(is_capture)
                    self.get_absent_pieces()
                    self.source_square_display = final_move.from_square
                    self.target_square_display = final_move.to_square

                    # 5. Cleanup Shared UI state
                    self.active_animation = None
                    self.pending_move = None
                    self.source_square = None
                    self.is_promoting = False
                    self.promotion_piece = None
        

    def engine_make_move(self):
        if self.engine is None:
            return

        with self.board_lock:
            # Check if it's the engine's turn
            is_engine_turn = (self.white_on_bottom and self.board.turn == chess.BLACK) or \
                            (not self.white_on_bottom and self.board.turn == chess.WHITE)

            # Guard: Only start if it's the engine's turn, we aren't already thinking, 
            # the game is active, and no animations are blocking.
            if (not is_engine_turn or 
                self.is_engine_thinking or 
                self.game_status != PLAYING or 
                self.active_animation is not None or 
                self.pending_move is not None):
                return

            # SETUP SEARCH (Still inside the lock)
            self.current_search_id = time.time()
            search_id = self.current_search_id
            board_copy = self.board.copy()
            self.is_engine_thinking = True

        # Start the thread OUTSIDE the lock to keep UI responsive
        thread = threading.Thread(target=self.run_engine, args=(board_copy, search_id))
        thread.daemon = True
        thread.start()

    def run_engine(self, board_copy, search_id):
        """ Runs in background thread with a thread-safe board snapshot """
        try:
            if not self.engine:
                return
            
            with self.board_lock:
                if self.is_force_quit_engine or self.game_status != PLAYING:
                    return

            # Start analysis on the copy
            with self.engine.analysis(board_copy, self.time_limit) as analysis:
                with self.board_lock:
                    self.current_analysis = analysis
                
                for info in analysis:
                    with self.board_lock:
                        if self.is_force_quit_engine or self.game_status != PLAYING \
                            or self.current_search_id != search_id:
                            analysis.stop()
                            break
                        self.search_info.update(info)    
                
                try:
                    result = analysis.wait()
                except (chess.engine.EngineError, chess.InvalidMoveError) as e:
                    print(f"Engine returned an invalid move or protocol error: {e}")
                    return
    
                if result.move:
                    with self.board_lock:
                        if self.is_force_quit_engine or self.game_status != PLAYING:
                            print("The game is terminated.")
                            return

                        if self.current_search_id != search_id:
                            print("Old analysis terminated.")
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
            with self.board_lock:
                if self.current_search_id == search_id:
                    self.current_analysis = None
                    self.is_engine_thinking = False

    def update_time(self):
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        with self.board_lock:
            if self.game_status != PLAYING:
                return
        
        if self.board.turn == chess.WHITE:
            self.white_clock = max(0, self.white_clock - delta_time)
        else:
            self.black_clock = max(0, self.black_clock - delta_time)

        if self.white_clock == 0 or self.black_clock == 0:
            with self.board_lock: # Protect status change
                self.update_game_status()
                self.generic_notification_sound.play()

    def update_game_status(self):
        # called when pushing and it doesnt need lock here
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

    def play_game(self):
        with self.board_lock:
            if self.game_status != PLAYING:
                self.board.set_fen(chess.STARTING_FEN)
                self.white_clock, self.black_clock = self.last_selected_time
                self.last_time = time.time()
                self.game_status = PLAYING
            
                #if not self.is_engine_thinking and self.current_analysis == None:

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

    def set_time_1_minute(self):
        with self.board_lock:
            if self.game_status != PLAYING:
                self.black_clock = TIME_1_MUNUTES
                self.white_clock = TIME_1_MUNUTES
                self.last_selected_time = (self.white_clock, self.black_clock)
                self.moves_to_go = MOVES_TO_GO_BLITZ
                self.time_limit = chess.engine.Limit(white_clock=self.white_clock, black_clock=self.black_clock, remaining_moves=self.moves_to_go)

    def set_time_5_minutes(self):
        with self.board_lock:
            if self.game_status != PLAYING:
                self.black_clock = TIME_5_MINUTES
                self.white_clock = TIME_5_MINUTES
                self.last_selected_time = (self.white_clock, self.black_clock)
                self.moves_to_go = MOVES_TO_GO_DEFAULT
                self.time_limit = chess.engine.Limit(white_clock=self.white_clock, black_clock=self.black_clock, remaining_moves=self.moves_to_go)
        
    def set_time_10_minutes(self):
        with self.board_lock:
            if self.game_status != PLAYING:
                self.black_clock = TIME_10_MINUTES
                self.white_clock = TIME_10_MINUTES
                self.last_selected_time = (self.white_clock, self.black_clock)
                self.moves_to_go = MOVES_TO_GO_DEFAULT
                self.time_limit = chess.engine.Limit(white_clock=self.white_clock, black_clock=self.black_clock, remaining_moves=self.moves_to_go)

    def change_board_orientation(self):
        with self.board_lock:
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


    def procces_animation_and_push_move(self, dt):
        if not self.active_animation:
            return

        # 1. Update animations (No lock needed for pixel math)
        self.active_animation.update(dt)
        if self.secondary_animation:
            self.secondary_animation.update(dt)

        # 2. Check if animation is finished
        if self.active_animation.is_done:
            # Wait for the Rook if it's still moving
            if self.secondary_animation and not self.secondary_animation.is_done:
                return

            # 3. Critical Section: Finalizing the Move
            with self.board_lock:
                # Re-check everything inside the lock to prevent race conditions
                if self.game_status != PLAYING or not self.pending_move:
                    # Clear animations if the game was stopped/ended while moving
                    self.active_animation = None
                    self.secondary_animation = None
                    self.pending_move = None
                    return

                # Determine turn logic
                is_human_turn = (self.white_on_bottom and self.board.turn == chess.WHITE) or \
                                (not self.white_on_bottom and self.board.turn == chess.BLACK)

                # If it's a human promotion, we DON'T push here. 
                # We wait for choose_promotion_piece to do it.
                if self.is_promoting and is_human_turn:
                    return

                # Execute the move
                move = self.pending_move
                self.source_square_display = move.from_square
                self.target_square_display = move.to_square

                is_capture = self.board.is_capture(move)
                self.board.push(move)

                # Update status, pieces, and sounds
                self.update_game_status()
                self.play_sound(is_capture)
                self.get_absent_pieces()

                # 4. Clean up state while still locked
                self.active_animation = None
                self.secondary_animation = None
                self.pending_move = None

    def shut_down_engine(self):
        with self.board_lock:
            self.is_force_quit_engine = True
            self.game_status = GAME_PAUSED

        # 1. Stop the current analysis first
        if self.current_analysis:
            try:
                self.current_analysis.stop()
            except:
                print("Error stoping analysis")

        # 2. Wait for the background thread to finish its loop (max 15 seconds)
        start_wait = time.time()
        while time.time() - start_wait < 15.0:
            with self.board_lock:
                if not self.is_engine_thinking:
                    break
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

    