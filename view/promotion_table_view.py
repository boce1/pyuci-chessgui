import pygame as pg
from config import *
import os
import chess 

class PromotionTableView:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pics_dir = os.path.join(current_dir, '..', 'pics')
        pics_dir = os.path.normpath(pics_dir)
        self.pieces_promotion_images = {
            'N': None, 'B': None, 'R': None, 'Q': None,
            'n': None, 'b': None, 'r': None, 'q': None
        }

        self.pieces_promotion_images['N'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-knight.png")), (PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT))
        self.pieces_promotion_images['B'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-bishop.png")), (PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT))
        self.pieces_promotion_images['R'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-rook.png")), (PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT))
        self.pieces_promotion_images['Q'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-queen.png")), (PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT))
        self.pieces_promotion_images['n'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-knight.png")), (PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT))
        self.pieces_promotion_images['b'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-bishop.png")), (PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT))
        self.pieces_promotion_images['r'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-rook.png")), (PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT))
        self.pieces_promotion_images['q'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-queen.png")), (PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT))

    def draw(self, win, is_promoting, playing_side):
        if(is_promoting):
            if playing_side == chess.WHITE:
                symbols = ['Q', 'R', 'N', 'B']
            else:
                symbols = ['q', 'r', 'n', 'b']

            # 2. Draw the background/container (optional but looks better)
            pg.draw.rect(win, GRAY, (PROMOTION_TABLE_X, PROMOTION_TABLE_Y, PROMOTION_TABLE_WIDTH, PROMOTION_TABLE_CELL_HEIGHT))

            # 3. Iterate and draw cells and pieces
            for i, symbol in enumerate(symbols):
                cell_x = PROMOTION_TABLE_X + i * PROMOTION_TABLE_CELL_WIDTH
                cell_y = PROMOTION_TABLE_Y

                # Draw cell border
                pg.draw.rect(win, BLACK, (cell_x, cell_y, PROMOTION_TABLE_CELL_WIDTH, PROMOTION_TABLE_CELL_HEIGHT), 1)

                # Draw the piece image
                img = self.pieces_promotion_images.get(symbol)
                if img:
                    win.blit(img, (cell_x, cell_y))
                #pg.draw.rect(win, BLACK, rect, 2)