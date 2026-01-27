from config import *
import pygame as pg

class Button:
    def __init__(self, x, y, width, height, action, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action
        self.font = pg.font.SysFont('Consolas', int(height * 0.3), bold=False)
        self.message = self.font.render(text, True, BLACK)
        self.color = WHITE

    def draw(self, win):
        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        pg.draw.rect(win, BLACK, (self.x, self.y, self.width, self.height), 3)
        win.blit(self.message, (self.x + self.width // 2 - self.message.get_width() //2,
                                self.y + self.height // 2 - self.message.get_height() // 2))

    def update_color_when_pressed(self, event, mouse_pos):
        x, y = mouse_pos

        # Check if mouse is hovering over the button
        if self.x <= x <= self.x + self.width and \
           self.y <= y <= self.y + self.height:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1: # Button is being held down
                self.color = GRAY
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

