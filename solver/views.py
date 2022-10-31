from collections import defaultdict
from django.shortcuts import render
from . import sudoku
from . import util

# Create your views here.
def index(request):

    final_grid = [[0] * 9 for i in range(9)]
    message = ""
    solved = False

    if request.method == "POST":
        # Convert data from form to be exceptable by sudoku.Sudoku class
        grid = [[int(request.POST[f'{i},{j}']) if request.POST[f'{i},{j}'] else 0 for j in range(9)] for i in range(9)]
        
        # Validate input
        try:
            solver = sudoku.SudokuSolver(sudoku.Sudoku(grid))
        
        # Input is invalid. Return grid given via post
        except sudoku.InvalidSudoku:
            message = 'Invalid sudoku'
            final_grid = grid

        else:
            assignment = solver.solve()
            
            # There is no solution. Return grid given via post
            if not assignment:
                message = 'No solution'
                final_grid = grid

            # There is a solution. Return resulted grid    
            else:
                final_grid = solver.grid(assignment)
                solved = True
    
    # Convert grid to list(tuple) where:
    # [0] - row, [1] - column, [2] - grid[i][j], [3] - additional classes for output purposes.
    # Ordered in a way: [0][0], [0][1] ...[0][8], [1][0]...[8][8]
    final = [(i, j, el, util.borders(i, j)) for i, row in enumerate(final_grid) for j, el in enumerate(row)]
    
    return render(request, "solver/index.html", {
        "grid": final,
        "message": message,
        "solved": solved,
        "page": 'solver:index',
    })

def diagonal(request):
    final_grid = [[0] * 9 for i in range(9)]
    message = ""
    solved = False

    if request.method == "POST":
        # Convert data from form to be exceptable by sudoku.Sudoku class
        grid = [[int(request.POST[f'{i},{j}']) if request.POST[f'{i},{j}'] else 0 for j in range(9)] for i in range(9)]
        
        # Validate input
        try:
            solver = sudoku.SudokuSolver(sudoku.DiagonalSudoku(grid))
        
        # Input is invalid. Return grid given via post
        except sudoku.InvalidSudoku:
            message = 'Invalid sudoku'
            final_grid = grid

        else:
            assignment = solver.solve()
            
            # There is no solution. Return grid given via post
            if not assignment:
                message = 'No solution'
                final_grid = grid

            # There is a solution. Return resulted grid    
            else:
                final_grid = solver.grid(assignment)
                solved = True
    
    # Convert grid to list(tuple) where:
    # [0] - row, [1] - column, [2] - grid[i][j], [3] - additional classes for output purposes.
    # Ordered in a way: [0][0], [0][1] ...[0][8], [1][0]...[8][8]
    final = [(i, j, el, util.x_borders(i, j)) for i, row in enumerate(final_grid) for j, el in enumerate(row)]
    
    return render(request, "solver/index.html", {
        "grid": final,
        "message": message,
        "solved": solved,
        "page": 'solver:x-sudoku'
    })