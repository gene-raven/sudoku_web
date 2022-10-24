# Sudoku Solver Web App

Made using Django framework. Extention of [sudoku-solver](https://github.com/gene-raven/sudoku-solver)
## Description:
There is one page on route 'solver' with sudoku grid 9x9 and 3 buttons.

*Solve* button. If there is a solution, it will be outputted in sudoku grid. Otherwise there will be displayed message: "No solution"  or "Invalid sudoku" if any given number is not within a constrain (1<= x <= 9).

*Clean* button. Returns input fuilds to the initial (after page loaded).

*New* button. Refreshes the page. All input fields are empty.
