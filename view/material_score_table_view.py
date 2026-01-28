import pygame as pg
import os
from config import *

class MaterialScoreTableView:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pics_dir = os.path.join(current_dir, '..', 'pics')
        pics_dir = os.path.normpath(pics_dir)
        self.pieces_material_images = {
            'P': None, 'N': None, 'B': None, 'R': None, 'Q': None,
            'p': None, 'n': None, 'b': None, 'r': None, 'q': None
        }

        self.pieces_material_images['P'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-pawn.png")), (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH))
        self.pieces_material_images['N'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-knight.png")), (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH))
        self.pieces_material_images['B'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-bishop.png")), (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH))
        self.pieces_material_images['R'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-rook.png")), (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH))
        self.pieces_material_images['Q'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "white-queen.png")), (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH))
        self.pieces_material_images['p'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-pawn.png")), (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH))
        self.pieces_material_images['n'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-knight.png")), (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH))
        self.pieces_material_images['b'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-bishop.png")), (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH))
        self.pieces_material_images['r'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-rook.png")), (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH))
        self.pieces_material_images['q'] = pg.transform.scale(pg.image.load(os.path.join(pics_dir, "black-queen.png")), (MATERIAL_SCORE_WIDTH, MATERIAL_SCORE_WIDTH))

        self.piece_img_cords = {
            'P' : (MATERIAL_SCORE_X, MATERIAL_WHITE_PAWN_Y),
            'N' : (MATERIAL_SCORE_X, MATERIAL_WHITE_KNIGHT_Y),
            'B' : (MATERIAL_SCORE_X, MATERIAL_WHITE_BISHOP_Y),
            'R' : (MATERIAL_SCORE_X, MATERIAL_WHITE_ROOK_Y),
            'Q' : (MATERIAL_SCORE_X, MATERIAL_WHITE_QUEEN_Y),
            'p' : (MATERIAL_SCORE_X, MATERIAL_BLACK_PAWN_Y),
            'n' : (MATERIAL_SCORE_X, MATERIAL_BLACK_KNIGHT_Y),
            'b' : (MATERIAL_SCORE_X, MATERIAL_BLACK_BISHOP_Y),
            'r' : (MATERIAL_SCORE_X, MATERIAL_BLACK_ROOK_Y),
            'q' : (MATERIAL_SCORE_X, MATERIAL_BLACK_QUEEN_Y)
        }

        self.font = pg.font.SysFont("Consolas", int(MATERIAL_SCORE_WIDTH * 0.6), bold=True)
        self.message_1_x = self.font.render("", True, BLACK)
        self.message_2_x = self.font.render("2x", True, BLACK)
        self.message_3_x = self.font.render("3x", True, BLACK)
        self.message_4_x = self.font.render("4x", True, BLACK)
        self.message_5_x = self.font.render("5x", True, BLACK)
        self.message_6_x = self.font.render("6x", True, BLACK)
        self.message_7_x = self.font.render("7x", True, BLACK)
        self.message_8_x = self.font.render("8x", True, BLACK)

    def get_message(self, num):
        if num == 1:
            return self.message_1_x
        elif num == 2:
            return self.message_2_x
        elif num == 3:
            return self.message_3_x
        elif num == 4:
            return self.message_4_x
        elif num == 5:
            return self.message_5_x
        elif num == 6:
            return self.message_6_x
        elif num == 7:
            return self.message_7_x
        elif num == 8:
            return self.message_8_x
        return None

    def draw_piece_material(self, win, piece_char, num):
        message = self.get_message(num)
        if message == None:
            return

        img = self.pieces_material_images[piece_char]
        cords = self.piece_img_cords[piece_char]
        win.blit(img, cords)
        win.blit(message, (cords[0] - message.get_width(), 
                                    cords[1] + img.get_height() // 2 - message.get_height() // 2))
        
    def draw(self, win, piece_map):
        for key in self.piece_img_cords.keys():
            self.draw_piece_material(win, key, piece_map[key])

