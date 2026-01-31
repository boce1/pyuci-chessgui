from config import *
import pygame as pg
import threading
import os
from .board_view import BoardView

class MainWindow:
    def __init__(self):
        pg.init()
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        pg.display.set_caption("Cincinnatus GUI")
        
        # Create window immediately
        self.window = pg.display.set_mode((self.width, self.height))
        
        # Setup loading state
        self.board_view = None
        self.loading_finished = False
        self.font = pg.font.SysFont("Consolas", 30)

        # Start the loading thread
        # daemon=True ensures the thread dies if you close the window
        loader = threading.Thread(target=self._load_task, daemon=True)
        loader.start()

        # The "Stay Alive" Loop
        # This keeps the splash screen drawing while the thread works
        self._run_splash()

    def _load_task(self):
        """This runs in the background. No pg.display calls allowed here!"""
        self.board_view = BoardView()
        self.loading_finished = True

    def _run_splash(self):
        """The Main Thread loop that prevents the 'Black Screen'."""
        clock = pg.time.Clock()
        while not self.loading_finished:
            # Handle events so Windows knows we are active
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    os._exit(0) # Force kill everything

            # Draw the loading screen
            self.window.fill(BACKGROUND_COLOR)
            font = pg.font.SysFont("Consolas", 30)
            loading_text = font.render("Loading the engine...", True, BLACK)
            text_rect = loading_text.get_rect(center=(self.width // 2, self.height // 2))
            self.window.blit(loading_text, text_rect)
            
            pg.display.flip()
            clock.tick(60) # Keep the UI smooth

    def draw(self):
        self.window.fill(BACKGROUND_COLOR)
        self.board_view.draw(self.window)
        pg.display.update()  # Update the display

    def run(self):
        clock = pg.time.Clock()
        running = True
        ctrl = self.board_view.controller
    
        while running:
            dt = clock.tick(FPS) / 1000.0 
            mouse_pos = pg.mouse.get_pos()
    
            # PROCESS ANIMATIONS
            ctrl.procces_animation_and_push_move(dt)
    
            # PROCESS EVENTS (ONE LOOP ONLY)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    with ctrl.board_lock:
                        ctrl.is_force_quit_engine = True
    
                # Handle UI Buttons
                self.board_view.change_side_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.change_side_button.execute_command(event, mouse_pos)
                self.board_view.one_minutes_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.one_minutes_button.execute_command(event, mouse_pos)
                self.board_view.five_minutes_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.five_minutes_button.execute_command(event, mouse_pos)
                self.board_view.ten_minutes_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.ten_minutes_button.execute_command(event, mouse_pos)
                self.board_view.pause_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.pause_button.execute_command(event, mouse_pos)
                self.board_view.play_button.update_color_when_pressed(event, mouse_pos)
                self.board_view.play_button.execute_command(event, mouse_pos)
    
                # Handle Board Interactions
                if ctrl.is_promoting:
                    ctrl.choose_promotion_piece(event, mouse_pos)
                else:
                    ctrl.handle_click(event, mouse_pos)
                # They are separate because promoting piece has its logic and it pushes the move
                # The animation 

            # RENDER & UPDATES
            self.draw()
            ctrl.update_time()
            ctrl.engine_make_move()
    
        pg.quit()
        ctrl.shut_down_engine()