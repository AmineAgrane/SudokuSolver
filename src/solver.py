"""
Sudoku Solver - Console Version
Solves a Sudoku puzzle using backtracking algorithm
"""

class SudokuSolver:

    def __init__(self, board):
        """
        Given an example board as arg, initialize the Sudoku solver with it. We use 0 for empty cells.
        """
        board = [row[:] for row in board]
        self.board = board

        # keep original
        self.original_board = board


    def is_valid(self, row, col, num):
        """Check if placing num at (row, col) is valid."""

        # Check row
        if num in self.board[row]:
            return False

        # Check column
        if num in [self.board[i][col] for i in range(9)]:
            return False

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == num:
                    return False

        return True

    def find_empty_cell(self):
        """Find an empty cell (a cell that have a value of 0)."""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return (i, j)
        return None

    def solve(self):
        """Solve the Sudoku puzzle using backtracking."""

        # get the coordinates of an empty cell
        # if no empty cell inside the board, the puzzle is solved
        empty = self.find_empty_cell()
        if not empty:
            return True

        # else
        row, col = empty

        # Try numbers 1-9
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                self.board[row][col] = num

                # Recursively try to solve
                if self.solve():
                    return True

                # Backtrack if solution not found
                self.board[row][col] = 0

        return False

    def print_board(self, title="Sudoku Board"):
        """Pretty print the Sudoku board."""
        print(f"\n{title}")
        print("=" * 37)
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("-" * 37)

            row_str = ""
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    row_str += " | "

                num = self.board[i][j]
                row_str += f" {num if num != 0 else '.'} "

            print(row_str)
        print("=" * 37)


def main():
    # Example Sudoku puzzle (0 represents empty cells)

    example_board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    # Create solver instance
    solver = SudokuSolver(example_board)

    # Print original puzzle
    solver.print_board("Original Puzzle")

    # Solve the puzzle
    print("\nSolving...")
    if solver.solve():
        solver.print_board("✓ Solved Puzzle")
    else:
        print("\n✗ No solution exists for this puzzle!")


if __name__ == "__main__":
    main()