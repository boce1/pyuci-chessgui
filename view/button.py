from config import *
import pygame as pg
import os

class Button:
    def __init__(self, x, y, width, height, action, text, type = DEFAULT_BUTTON):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action
        self.font = pg.font.SysFont('Consolas', int(height * 0.3), bold=False)
        self.message = self.font.render(text, True, BLACK)
        self.color = WHITE

        current_dir = os.path.dirname(os.path.abspath(__file__))
        pics_dir = os.path.join(current_dir, '..', 'pics')
        pics_dir = os.path.normpath(pics_dir)
        self.img = pg.transform.scale(pg.image.load(os.path.join(pics_dir, type)), (self.width, self.height)).convert_alpha()
        self.img.set_alpha(150) # ((150 / 256) * 100) % transparent

    def draw(self, win):
        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        win.blit(self.img, (self.x, self.y))
        win.blit(self.message, (self.x + self.width // 2 - self.message.get_width() // 2,
                                self.y + self.height // 2 - self.message.get_height() // 2))
        pg.draw.rect(win, BLACK, (self.x, self.y, self.width, self.height), 3)

    def update_color_when_pressed(self, event, mouse_pos):
        x, y = mouse_pos

        # Check if mouse is hovering over the button
        if self.x <= x <= self.x + self.width and \
           self.y <= y <= self.y + self.height:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1: # Button is being held down
                self.color = DARK_GRAY
        else:
            self.color = WHITE
    

    def is_clicked_mouseup_event(self, event, mouse_pos):
        x = mouse_pos[0]
        y = mouse_pos[1]

        if self.x <= x <= self.x + self.width and \
            self.y <= y <= self.y + self.height:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                return True
            
        return False
    
    def execute_command(self, event, mouse_pos):
        if self.is_clicked_mouseup_event(event, mouse_pos):
            self.color = WHITE
            self.action()

