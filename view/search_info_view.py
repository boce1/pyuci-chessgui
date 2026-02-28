from config import *
from controller.search_info import SearchInfo
import pygame as pg

class SearchInfoView:
    def __init__(self):
        self.search_info = None
        self.font_size = int(SQUARE_SIZE * 0.3)
        self.font = pg.font.SysFont('Consolas', self.font_size, bold=False)

    def draw_box(self, win):
        # Define the inner gap (twice smaller than GAP_INFO)
        sg = GAP_INFO // 2
        x, y, w, h = SEARCH_INFO_X, SEARCH_INFO_Y, SEARCH_INFO_WIDTH, SEARCH_INFO_HEIGHT

        # Draw the inner border (to connect the lines to)
        pg.draw.rect(win, GRAY, (SEARCH_INFO_X, SEARCH_INFO_Y, SEARCH_INFO_WIDTH, SEARCH_INFO_HEIGHT), sg)
        pg.draw.rect(win, BLACK, (x + sg, y + sg, w - 2 * sg, h - 2 * sg), 2)

        # Draw Corner Lines (Outer to Inner)
        # Using the -1/+1 offset to prevent the lines from poking through the outer border
        pg.draw.line(win, BLACK, (x + 1, y + 1), (x + sg, y + sg), 2) # Top-Left
        pg.draw.line(win, BLACK, (x + w - 1, y + 1), (x + w - sg, y + sg), 2) # Top-Right
        pg.draw.line(win, BLACK, (x + 1, y + h - 1), (x + sg, y + h - sg), 2) # Bottom-Left
        pg.draw.line(win, BLACK, (x + w - 1, y + h - 1), (x + w - sg, y + h - sg), 2) # Bottom-Right

    def draw(self, win, search_info):
        pg.draw.rect(win, WHITE, (SEARCH_INFO_X, SEARCH_INFO_Y, SEARCH_INFO_WIDTH, SEARCH_INFO_HEIGHT))
        self.draw_box(win)
        pg.draw.rect(win, BLACK, (SEARCH_INFO_X, SEARCH_INFO_Y, SEARCH_INFO_WIDTH, SEARCH_INFO_HEIGHT), 2)

        current_y = SEARCH_INFO_Y + GAP_INFO
        max_w = SEARCH_INFO_WIDTH - (GAP_INFO * 2)

        # 2. Draw Depth
        if search_info.depth != None:
            depth_surf = self.font.render(f"Depth {search_info.depth}", True, BLACK)
            win.blit(depth_surf, (SEARCH_INFO_X + GAP_INFO, current_y))
            current_y += depth_surf.get_height()

        # 3. Draw Eval
        if search_info.eval != None:
            if search_info.eval < 0:
                eval_surf = self.font.render(f"Eval {search_info.eval}. The player has adventage", True, BLACK)
            elif search_info.eval > 0:
                eval_surf = self.font.render(f"Eval {search_info.eval}. The engine has adventage", True, BLACK)
            else:
                eval_surf = self.font.render(f"Eval {search_info.eval}", True, BLACK)
            win.blit(eval_surf, (SEARCH_INFO_X + GAP_INFO, current_y))
            current_y += eval_surf.get_height() + 5

        # 4. Draw Principle Variation (PV) with Auto-Wrap
        if search_info.principle_variation != None:
            pv_list = [move.uci() for move in search_info.principle_variation]
            
            line_text = "PV "
            for move in pv_list:
                # Test if adding the next move exceeds the width
                test_line = line_text + move + " "
                test_size = self.font.size(test_line)[0]

                if test_size < max_w:
                    line_text = test_line
                else:
                    # Render current line and start a new one
                    pv_surf = self.font.render(line_text, True, BLACK)
                    win.blit(pv_surf, (SEARCH_INFO_X + GAP_INFO, current_y))
                    
                    current_y += pv_surf.get_height()
                    line_text = move + " " # Start new line with the move that didn't fit

                    # Safety check: Stop drawing if we exceed the box height
                    if current_y + self.font_size > SEARCH_INFO_Y + SEARCH_INFO_HEIGHT:
                        return

            # Render the final remaining bit of text
            if line_text:
                final_pv_surf = self.font.render(line_text, True, BLACK)
                win.blit(final_pv_surf, (SEARCH_INFO_X + GAP_INFO, current_y))

