import pygame as pg
import os
import chess
from controller import get_resource_path
from config import *

class PromotionTableView:
    def __init__(self):
        self.pieces_promotion_images = {}
        self.load_resources()

    def load_resources(self):
        """Standardized resource loading using the universal path helper."""
        # Pieces used in promotion
        mapping = {
            'Q': "white-queen.png", 'R': "white-rook.png", 
            'N': "white-knight.png", 'B': "white-bishop.png",
            'q': "black-queen.png", 'r': "black-rook.png", 
            'n': "black-knight.png", 'b': "black-bishop.png"
        }

        for symbol, filename in mapping.items():
            # 1. Use the helper for absolute pathing
            path = get_resource_path(os.path.join('pics', filename))

            # 2. Check if file exists to avoid Pygame errors
            if not os.path.exists(path):
                print(f"Error: Promotion image missing at {path}")
                continue

            # 3. Load, convert, and scale
            img = pg.image.load(path).convert_alpha()
            self.pieces_promotion_images[symbol] = pg.transform.scale(
                img, (PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT)
            )

    def draw(self, win, is_promoting, turn):
        if not is_promoting:
            return

        # 1. Dim the background slightly to highlight the promotion choice
        # This creates a "modal" feel
        overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 30))  # Semi-transparent black
        win.blit(overlay, (0, 0))

        # 2. Select pieces based on turn
        symbols = ['Q', 'R', 'N', 'B'] if turn == chess.WHITE else ['q', 'r', 'n', 'b']

        # 3. Draw Table Container
        container_rect = (PROMOTION_TABLE_X, PROMOTION_TABLE_Y, PROMOTION_TABLE_WIDTH, PROMOTION_TABLE_CELL_HEIGHT)
        pg.draw.rect(win, WHITE, container_rect)  # Solid background
        pg.draw.rect(win, BLACK, container_rect, 2) # Outer border

        # 4. Iterate and draw cells
        mouse_pos = pg.mouse.get_pos()
        
        for i, symbol in enumerate(symbols):
            cell_x = PROMOTION_TABLE_X + i * PROMOTION_TABLE_CELL_WIDTH
            cell_y = PROMOTION_TABLE_Y
            cell_rect = pg.Rect(cell_x, cell_y, PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT)

            # Hover effect: Highlight the cell if mouse is over it
            if cell_rect.collidepoint(mouse_pos):
                pg.draw.rect(win, HIGHLIGHT_COLOR, cell_rect)

            # Draw cell border
            pg.draw.rect(win, BLACK, cell_rect, 1)

            # Draw piece
            img = self.pieces_promotion_images.get(symbol)
            if img:
                win.blit(img, (cell_x, cell_y))