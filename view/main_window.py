from config import *
import pygame as pg
import threading
from controller.file_path import *
from .board_view import BoardView

class MainWindow:
    def __init__(self):
        pg.init()
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        pg.display.set_caption("Cincinnatus GUI")
        
        # Create window immediately
        self.window = pg.display.set_mode((self.width, self.height))
        
        # Load the image and set it as the icon
        icon_path = get_resource_path(os.path.join("pics", "icon.png"))
        try:
            icon_surface = pg.image.load(icon_path)
            pg.display.set_icon(icon_surface)
        except pg.error:
            print(f"Could not find icon at {icon_path}")

        # Setup loading state
        self.board_view = None
        self.loading_finished = threading.Event()
        self.font = pg.font.SysFont("Consolas", 30)

        # Start the loading thread
        # daemon=True ensures the thread dies if you close the window
        loader = threading.Thread(target=self._load_task, daemon=True)
        loader.start()

        # The "Stay Alive" Loop
        # This keeps the splash screen drawing while the thread works
        self._run_splash()

        raw_img = pg.image.load(get_resource_path(os.path.join("pics", "texture-background.bmp")))
        converted_img = raw_img.convert()
        self.background = pg.transform.scale(converted_img, (SCREEN_WIDTH, SCREEN_HEIGHT))  

    def _load_task(self):
        """This runs in the background. No pg.display calls allowed here"""
        self.board_view = BoardView()
        self.loading_finished.set()

    def _run_splash(self):
        """The Main Thread loop that prevents the 'Black Screen'."""
        clock = pg.time.Clock()
        while not self.loading_finished.is_set():
            # Handle events so Windows knows the app is responsive
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return

            # Clear the screen
            self.window.fill(BACKGROUND_COLOR)
            
            # Render and center the text
            loading_text = self.font.render("Loading the engine...", True, BLACK)
            
            # Draw to the window
            self.window.blit(loading_text, (self.width // 2 - loading_text.get_width() // 2,
                                            self.height // 2 - loading_text.get_height() // 2))
            
            # Use flip to swap buffers and force Windows to map the window
            pg.display.flip()
            pg.event.pump()
            # Keep it at 60 FPS to stay smooth without hogging the CPU
            clock.tick(FPS)

    def draw(self):
        # self.window.fill(BACKGROUND_COLOR)
        self.window.blit(self.background, (0, 0))
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

            #  RENDER & UPDATES
            self.draw()
            ctrl.update_time()
            ctrl.engine_make_move()
    
        pg.quit()
        ctrl.shut_down_engine()