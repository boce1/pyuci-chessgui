import chess
import chess.engine as engine
import os
import pygame as pg
import threading
from config import *

class BoardController:
    def __init__(self):
        self.board = chess.Board()
        self.engine = None
        self.load_engine()
        self.white_on_bottom = True # Default orientation
        self.source_square = None
        self.legal_moves_for_source_square = []
        self.is_engine_thinking = False

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

    def handle_click(self, event, mouse_pos):
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
                return

            # Check if the clicked square is one of the legal destinations
            move_to_make = None
            for m in self.legal_moves_for_source_square:
                if m.to_square == square:
                    move_to_make = m
                    break
                
            if move_to_make:
                self.board.push(move_to_make)
                self.source_square = None # Reset for next move
                self.legal_moves_for_source_square = []
            else:
                # If user clicks a different piece of their own, change selection instead
                new_piece = self.board.piece_at(square)
                if new_piece and new_piece.color == self.board.turn:
                    self.source_square = square
                    self.get_legal_moves_for_source_square()
                else:
                    # Clicked an illegal square or empty space, deselect
                    self.source_square = None
                    self.legal_moves_for_source_square = []

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
            # The engine calculates here (GUI stays responsive)
            result = self.engine.play(self.board, chess.engine.Limit(time=1.0)) # Reduced time for testing

            if result.move is not None:
                # Important: We push the move back to the board
                self.board.push(result.move)
        finally:
            # Reset the flag so the engine can move again next turn
            self.is_engine_thinking = False

    def change_turn(self):
        self.board.turn = not self.board.turn

    def shut_down_engine(self):
        if self.engine:
            self.engine.quit()

    