import pygame as pg

class MoveAnimation:
    def __init__(self, piece_symbol, start_pos, end_pos, duration=0.15):
        self.piece_symbol = piece_symbol
        self.start_pos = pg.Vector2(start_pos)
        self.end_pos = pg.Vector2(end_pos)
        self.current_pos = pg.Vector2(start_pos)
        self.duration = duration
        self.elapsed = 0
        self.is_done = False

    def update(self, dt):
        self.elapsed += dt
        t = min(1.0, self.elapsed / self.duration)
        # "Ease out" curve for smoother landing
        t = t * (2 - t) 
        self.current_pos = self.start_pos.lerp(self.end_pos, t)
        if t >= 1.0:
            self.is_done = True