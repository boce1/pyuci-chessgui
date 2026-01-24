import chess
import chess.engine as engine
import os
import pygame as pg

class BoardController:
    def __init__(self):
        self.board = chess.Board()
        self.engine = None
        self.load_engine()
        self.white_on_bottom = True # Default orientation

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

    def shut_down_engine(self):
        if self.engine:
            self.engine.quit()