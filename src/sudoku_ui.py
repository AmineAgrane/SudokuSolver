"""
Sudoku Game with GUI using Pygame
Features: Play Sudoku, timer, solve button, input validation
"""

import pygame
import sys
import time
import random


class SudokuGame:

    def __init__(self):
        pygame.init()

        # Constants
        self.WIDTH = 630
        self.HEIGHT = 700
        self.GRID_SIZE = 540
        self.CELL_SIZE = self.GRID_SIZE // 9
        self.GRID_OFFSET = 50

        # Colors
        self.WHITE = (248, 248, 250)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.BLUE = (52, 152, 219)
        self.RED = (231, 76, 60)
        self.GREEN = (46, 204, 113)
        self.LIGHT_BLUE = (200, 220, 255)

        # Setup display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Sudoku Game")

        # Fonts
        self.num_font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 32)



        # Add after self.LIGHT_BLUE definition
        self.ARROW_SIZE = 20
        self.difficulties = ["Easy", "Medium", "Hard"]
        self.difficulty_index = 1  # Start at Medium (index 1)
        self.difficulty = self.difficulties[self.difficulty_index].lower()

        # Game state
        #self.difficulty = "medium"  # default
        self.selected = None
        self.board = None
        self.original_board = None
        self.start_time = None
        self.full_solution = None
        self.solve_stack = []
        self.generate_puzzle()


        self.visualize_mode = False
        self.auto_solve = False
        self.last_step_time = 0
        self.step_delay = 0.3  # seconds per step

    def generate_puzzle(self):
        """Generate a completely new random Sudoku puzzle with unique solution."""
        # Step 1: Generate a full valid board
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.original_board = [row[:] for row in self.board]

        self.fill_diagonal_boxes()
        # ← MOVE THIS LINE HERE:
        self.original_board = [row[:] for row in self.board]  # Save FULL solution
        self.solve_from(0, 0)  # Fill the rest using backtracking
        #self.original_board = [row[:] for row in self.board]  # Save solved

        # save the full solution
        self.full_solution = [row[:] for row in self.board]

        # Step 2: Remove cells to make puzzle (keep unique solution)
        if self.difficulty == "easy":
            self.remove_cells_symmetrically(35)
        elif self.difficulty == "medium":
            self.remove_cells_symmetrically(45)
        elif self.difficulty == "hard":
            self.remove_cells_symmetrically(55)

        #Puzzle with holes
        self.original_board = [row[:] for row in self.board]
        self.solve_from(0, 0)
        self.start_time = time.time()

    def fill_diagonal_boxes(self):
        """Fill the three diagonal 3x3 boxes with random valid numbers."""
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            idx = 0
            for i in range(3):
                for j in range(3):
                    self.board[box + i][box + j] = nums[idx]
                    idx += 1

    def solve_from(self, row, col):
        """Recursive backtracking to fill non-diagonal cells."""
        if col == 9:
            row += 1
            col = 0
        if row == 9:
            return True

        # Skip diagonal 3x3 boxes if already filled
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        if box_row == box_col and self.board[row][col] != 0:
            return self.solve_from(row, col + 1)

        # Try numbers 1-9
        nums = list(range(1, 10))
        random.shuffle(nums)
        for num in nums:
            if self.is_valid_move(self.board, row, col, num):
                self.board[row][col] = num
                if self.solve_from(row, col + 1):
                    return True
                self.board[row][col] = 0
        return False

    def solve_step(self):
        """Perform ONE step of backtracking. Return True if solved."""
        # Initialize stack on first call
        if not self.solve_stack:
            empty = self.find_empty_cell(self.board)
            if empty:
                self.solve_stack.append(empty)
            else:
                return True  # Already solved

        if not self.solve_stack:
            return True

        row, col = self.solve_stack[-1]
        start_num = self.board[row][col] + 1 if self.board[row][col] > 0 else 1

        for num in range(start_num, 10):
            if self.is_valid_move(self.board, row, col, num):
                self.board[row][col] = num
                next_empty = self.find_empty_cell(self.board)
                if next_empty:
                    self.solve_stack.append(next_empty)
                else:
                    return True  # Solved
                return False  # Step done

        # Backtrack
        self.board[row][col] = 0
        self.solve_stack.pop()
        return False

    def count_solutions(self, board):
        """Count number of solutions (for uniqueness check)."""
        empty = self.find_empty_cell(board)
        if not empty:
            return 1
        row, col = empty
        count = 0
        for num in range(1, 10):
            if self.is_valid_move(board, row, col, num):
            # self.is_valid_in_board(board, row, col, num):
                board[row][col] = num
                count += self.count_solutions(board)
                board[row][col] = 0
                if count > 1:
                    return count  # Early exit if more than 1
        return count

    def find_empty_cell(self, board):
        """Return (row, col) of first empty cell in board, or None."""
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None

    def remove_cells_symmetrically(self, cells_to_remove):
        """Remove cells in pairs (symmetric) to keep puzzle nice, ensure unique solution."""
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)

        removed = 0
        while removed < cells_to_remove and positions:
            row, col = positions.pop()
            if self.board[row][col] == 0:
                continue

            # Symmetric pair
            sym_row, sym_col = 8 - row, 8 - col

            # Backup values
            backup = self.board[row][col]
            backup_sym = self.board[sym_row][sym_col] if (row != sym_row or col != sym_col) else None

            # Try removing
            self.board[row][col] = 0
            if row != sym_row or col != sym_col:
                self.board[sym_row][sym_col] = 0

            # Check if still unique
            test_board = [r[:] for r in self.board]
            if self.count_solutions(test_board) == 1:
                removed += 2 if (row != sym_row or col != sym_col) else 1
            else:
                # Revert
                self.board[row][col] = backup
                if row != sym_row or col != sym_col:
                    self.board[sym_row][sym_col] = backup_sym

    def is_valid_move(self, board, row, col, num):
        """Check if num can be placed at board[row][col]. Works on any board."""
        if num in board[row]: return False
        if num in [board[i][col] for i in range(9)]: return False
        br, bc = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[br + i][bc + j] == num: return False
        return True

    def solve(self):
        """Solve the Sudoku puzzle using backtracking."""
        empty = self.find_empty_cell(self.board)

        if not empty:
            return True

        row, col = empty

        for num in range(1, 10):
            if self.is_valid_move(self.board, row, col, num):
                self.board[row][col] = num

                if self.solve():
                    return True

                self.board[row][col] = 0

        return False

    def is_complete(self):
        """Check if the puzzle is completely and correctly solved."""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return False
                # Check if current number is valid
                num = self.board[i][j]
                self.board[i][j] = 0
                if not self.is_valid_move(self.board, i, j, num):
                    self.board[i][j] = num
                    return False
                self.board[i][j] = num
        return True

    # UI Functions

    def draw_grid(self):
        """Draw the Sudoku grid."""
        # Draw cells
        for i in range(9):
            for j in range(9):
                x = self.GRID_OFFSET + j * self.CELL_SIZE
                y = self.GRID_OFFSET + i * self.CELL_SIZE

                # Highlight selected cell
                if self.selected == (i, j):
                    pygame.draw.rect(self.screen, self.LIGHT_BLUE,
                                     (x, y, self.CELL_SIZE, self.CELL_SIZE))

                # Draw cell border
                pygame.draw.rect(self.screen, self.BLACK,
                                 (x, y, self.CELL_SIZE, self.CELL_SIZE), 1)

                # Draw number
                if self.board[i][j] != 0:
                    num = self.board[i][j]

                    # Visual solve: highlight current cell being tried
                    if (self.visualize_mode and self.solve_stack and(i, j) == self.solve_stack[-1] and self.original_board[i][j] == 0):
                        color = self.RED  # Current trial
                    elif (self.visualize_mode and self.solve_stack and len(self.solve_stack) > 1 and (i, j) == self.solve_stack[-2]):
                        color = self.GREEN  # Previous (locked in)
                    elif self.original_board[i][j] != 0:
                        color = self.BLACK
                    else:
                        color = self.BLUE


                    # Different color: BLACK for original, BLUE for user input
                    #if self.original_board[i][j] != 0:
                    #    color = self.BLACK  # Original numbers
                        # else:
                    #   color = self.BLUE   # User input

                    text = self.num_font.render(str(int(num)), True, color)
                    text_rect = text.get_rect(center=(x + self.CELL_SIZE//2, y + self.CELL_SIZE//2))
                    self.screen.blit(text, text_rect)

        # Draw thick lines for 3x3 boxes
        for i in range(10):
            thickness = 4 if i % 3 == 0 else 1
            # Horizontal lines
            pygame.draw.line(self.screen, self.BLACK,
                             (self.GRID_OFFSET, self.GRID_OFFSET + i * self.CELL_SIZE),
                             (self.GRID_OFFSET + self.GRID_SIZE, self.GRID_OFFSET + i * self.CELL_SIZE),
                             thickness)
            # Vertical lines
            pygame.draw.line(self.screen, self.BLACK,
                             (self.GRID_OFFSET + i * self.CELL_SIZE, self.GRID_OFFSET),
                             (self.GRID_OFFSET + i * self.CELL_SIZE, self.GRID_OFFSET + self.GRID_SIZE),
                             thickness)

    def draw_buttons(self):
        """Draw control buttons."""
        # Solve button
        solve_rect = pygame.Rect(50, 610, 150, 50)
        pygame.draw.rect(self.screen, self.GREEN, solve_rect)
        pygame.draw.rect(self.screen, self.BLACK, solve_rect, 2)
        solve_text = self.button_font.render("Solve", True, self.WHITE)
        self.screen.blit(solve_text, solve_text.get_rect(center=solve_rect.center))

        # New Game button
        new_rect = pygame.Rect(220, 610, 150, 50)
        pygame.draw.rect(self.screen, self.BLUE, new_rect)
        pygame.draw.rect(self.screen, self.BLACK, new_rect, 2)
        new_text = self.button_font.render("New Game", True, self.WHITE)
        self.screen.blit(new_text, new_text.get_rect(center=new_rect.center))

        # Clear button
        clear_rect = pygame.Rect(390, 610, 150, 50)
        pygame.draw.rect(self.screen, self.RED, clear_rect)
        pygame.draw.rect(self.screen, self.BLACK, clear_rect, 2)
        clear_text = self.button_font.render("Clear", True, self.WHITE)
        self.screen.blit(clear_text, clear_text.get_rect(center=clear_rect.center))


        return solve_rect, new_rect, clear_rect

    def draw_timer(self):
        """Draw the elapsed time."""
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        timer_text = self.small_font.render(f"Time: {minutes:02d}:{seconds:02d}",
                                            True, self.BLACK)
        self.screen.blit(timer_text, (400, 5))

    def draw_title2(self):
        """Draw the game title."""
        title_text = self.small_font.render("SUDOKU", True, self.BLACK)
        self.screen.blit(title_text, (50, 5))

    def draw_title(self):
        """Draw the game title with difficulty selector."""
        title_text = self.small_font.render("SUDOKU", True, self.BLACK)
        self.screen.blit(title_text, (50, 5))

        # Difficulty selector (right of title)
        diff_x = 220
        diff_y = 10

        # Left arrow
        left_arrow = pygame.Rect(diff_x, diff_y, self.ARROW_SIZE, self.ARROW_SIZE)
        pygame.draw.polygon(self.screen, self.GRAY if self.difficulty_index == 0 else self.BLUE,
                            [(diff_x + self.ARROW_SIZE, diff_y),
                             (diff_x, diff_y + self.ARROW_SIZE // 2),
                             (diff_x + self.ARROW_SIZE, diff_y + self.ARROW_SIZE)])

        # Difficulty text
        diff_text = self.small_font.render(self.difficulties[self.difficulty_index], True, self.BLACK)
        diff_rect = diff_text.get_rect(center=(diff_x + 80, diff_y + self.ARROW_SIZE // 2))
        self.screen.blit(diff_text, diff_rect)

        # Right arrow
        right_arrow = pygame.Rect(diff_x + 140, diff_y, self.ARROW_SIZE, self.ARROW_SIZE)
        pygame.draw.polygon(self.screen, self.GRAY if self.difficulty_index == 2 else self.BLUE,
                            [(diff_x + 140, diff_y),
                             (diff_x + 140 + self.ARROW_SIZE, diff_y + self.ARROW_SIZE // 2),
                             (diff_x + 140, diff_y + self.ARROW_SIZE)])

        return left_arrow, right_arrow

    def handle_click(self, pos, solve_rect, new_rect, clear_rect, left_arrow, right_arrow):
        x, y = pos

        # Grid click
        if (self.GRID_OFFSET <= x <= self.GRID_OFFSET + self.GRID_SIZE and
                self.GRID_OFFSET <= y <= self.GRID_OFFSET + self.GRID_SIZE):
            col = (x - self.GRID_OFFSET) // self.CELL_SIZE
            row = (y - self.GRID_OFFSET) // self.CELL_SIZE
            self.selected = (row, col)

        # === BUTTONS: Check in this order ===
        elif solve_rect.collidepoint(pos):

            if not self.visualize_mode:
                # Reset to puzzle
                self.board = [row[:] for row in self.original_board]
                # Reset solver state
                self.solve_stack = []
                self.visualize_mode = True
                self.auto_solve = True
                self.last_step_time = time.time()

            else:
                # Instant solve if already visualizing
                self.board = [row[:] for row in self.original_board]
                self.solve()
                self.visualize_mode = False
                self.auto_solve = False


            #self.board = [row[:] for row in self.original_board]
            #self.solve()

        elif new_rect.collidepoint(pos):
            self.generate_puzzle()  # This now uses self.difficulty

        elif clear_rect.collidepoint(pos):
            for i in range(9):
                for j in range(9):
                    if self.original_board[i][j] == 0:
                        self.board[i][j] = 0

        # Arrow clicks for difficulty
        elif left_arrow.collidepoint(pos) and self.difficulty_index > 0:
            self.difficulty_index -= 1
            self.difficulty = self.difficulties[self.difficulty_index].lower()
        elif right_arrow.collidepoint(pos) and self.difficulty_index < 2:
            self.difficulty_index += 1
            self.difficulty = self.difficulties[self.difficulty_index].lower()

    def handle_key(self, key):
        """Handle keyboard input."""
        if self.selected:
            row, col = self.selected

            # Handle arrow keys (always available)
            if key == pygame.K_UP and row > 0:
                self.selected = (row - 1, col)
            elif key == pygame.K_DOWN and row < 8:
                self.selected = (row + 1, col)
            elif key == pygame.K_LEFT and col > 0:
                self.selected = (row, col - 1)
            elif key == pygame.K_RIGHT and col < 8:
                self.selected = (row, col + 1)

            # Only allow number input in cells that were originally empty
            elif self.original_board[row][col] == 0:
                # Handle number keys from main keyboard
                if pygame.K_1 <= key <= pygame.K_9:
                    num = key - pygame.K_0
                    self.board[row][col] = num
                # Handle numpad keys separately with correct mapping
                elif pygame.K_KP1 <= key <= pygame.K_KP9:
                    # Map numpad keys correctly
                    numpad_map = {
                        pygame.K_KP0: 0, pygame.K_KP1: 1, pygame.K_KP2: 2,
                        pygame.K_KP3: 3, pygame.K_KP4: 4, pygame.K_KP5: 5,
                        pygame.K_KP6: 6, pygame.K_KP7: 7, pygame.K_KP8: 8,
                        pygame.K_KP9: 9
                    }
                    self.board[row][col] = numpad_map[key]
                elif key in (pygame.K_DELETE, pygame.K_BACKSPACE, pygame.K_0, pygame.K_KP0):
                    self.board[row][col] = 0

    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        running = True

        while running:
            self.screen.fill(self.WHITE)

            # Draw game elements
            left_arrow, right_arrow = self.draw_title()
            self.draw_timer()
            self.draw_grid()
            solve_rect, new_rect, clear_rect = self.draw_buttons()

            # Check if puzzle is complete
            if self.is_complete():
                complete_bg = pygame.Rect(200, 575, 200, 35)
                pygame.draw.rect(self.screen, self.GREEN, complete_bg, border_radius=8)
                complete_text = self.small_font.render("COMPLETED!", True, self.WHITE)
                self.screen.blit(complete_text, complete_text.get_rect(center=complete_bg.center))


            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, solve_rect, new_rect, clear_rect, left_arrow, right_arrow)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)

            pygame.display.flip()
            clock.tick(60)

            # Auto-step visual solver
            if self.auto_solve and self.visualize_mode:
                now = time.time()
                if now - self.last_step_time >= self.step_delay:
                    if self.solve_step():
                        self.auto_solve = False  # Done
                    self.last_step_time = now

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SudokuGame()
    game.run()
