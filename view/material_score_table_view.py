import pygame as pg
import os
from controller import get_resource_path
from config import *

class MaterialScoreTableView:
    def __init__(self):
        pg.font.init()
        self.font = pg.font.SysFont("Consolas", int(MATERIAL_SCORE_WIDTH * 0.6), bold=True)
        
        self.pieces_material_images = {}
        self.piece_img_coords = {}
        
        self.load_resources()

    def load_resources(self):
        """Data-driven loading using the universal resource path helper."""
        # Mapping symbols to filenames
        mapping = {
            'P': "white-pawn.png",   'N': "white-knight.png", 'B': "white-bishop.png",
            'R': "white-rook.png",   'Q': "white-queen.png",
            'p': "black-pawn.png",   'n': "black-knight.png", 'b': "black-bishop.png",
            'r': "black-rook.png",   'q': "black-queen.png"
        }

        # Mapping symbols to Y coordinates
        y_coords = {
            'P': MATERIAL_WHITE_PAWN_Y,   'N': MATERIAL_WHITE_KNIGHT_Y, 
            'B': MATERIAL_WHITE_BISHOP_Y, 'R': MATERIAL_WHITE_ROOK_Y, 
            'Q': MATERIAL_WHITE_QUEEN_Y,
            'p': MATERIAL_BLACK_PAWN_Y,   'n': MATERIAL_BLACK_KNIGHT_Y, 
            'b': MATERIAL_BLACK_BISHOP_Y, 'r': MATERIAL_BLACK_ROOK_Y, 
            'q': MATERIAL_BLACK_QUEEN_Y
        }

        for symbol, filename in mapping.items():
            # Get the path using the helper
            path = get_resource_path(os.path.join('pics', filename))

            # Safety check: avoid crashing if a file is missing
            if not os.path.exists(path):
                print(f"Warning: Missing material icon for {symbol} at {path}")
                continue

            #  Load, convert, and scale
            img = pg.image.load(path).convert_alpha()
            self.pieces_material_images[symbol] = pg.transform.smoothscale(
                img, (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH)
            )

            # Store coordinates
            self.piece_img_coords[symbol] = (MATERIAL_SCORE_X, y_coords[symbol])

    def draw_piece_material(self, win, piece_char, num):
        """Draws the piece icon and the quantity multiplier (e.g., 2x)."""
        if num <= 0:
            return

        img = self.pieces_material_images[piece_char]
        coords = self.piece_img_coords[piece_char]
        
        # 1. Draw the piece icon
        win.blit(img, coords)

        # 2. Draw the multiplier text (only if > 1)
        if num > 1:
            text_str = f"{num}x"
            message = self.font.render(text_str, True, BLACK)
            
            # Position text to the left of the image, vertically centered
            text_x = coords[0] - message.get_width() - 5  # 5px padding
            text_y = coords[1] + (img.get_height() // 2) - (message.get_height() // 2)
            win.blit(message, (text_x, text_y))

    def draw(self, win, absent_pieces_map):
        """Matches BoardView's signature, iterating through the pieces."""
        for symbol in self.piece_img_coords.keys():
            quantity = absent_pieces_map.get(symbol, 0)
            self.draw_piece_material(win, symbol, quantity)