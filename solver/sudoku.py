# -*- coding: utf-8 -*-

class Variable():

    def __init__(self, i: int, j: int, initial: bool):
        '''
        Create a new variable with position (i, j) and flag initial

        :param i: horisontal position of the sell, starts from 0
        :type i: int
        :param j: vertical position of the sell, starts from 0
        :type j: int
        :param initial: flag indicating if variable is initial, i.e. set from a start
        :type initial: bool
        '''
        self.i = i
        self.j = j
        self.initial = initial
        self.box = (i // 3) * 3 + (j // 3) 
        
    def __hash__(self):
        return hash((self.i, self.j))
    
    def __eq__(self, other):
        return ((self.i == other.i) and (self.j == other.j))
        
    def __str__(self):
        return f'[{self.i}, {self.j}] in box {self.box}'


class Sudoku():
    
    def __init__(self, grid, num_rows: int = 9, num_columns: int = 9):
        '''
        Initialize sudoku

        :param grid: sudoku grid
        :type grid: list[list[int]]
        :param num_rows: number of rows
        :type num_rows: int | 9
        :param num_columns:  number of columns
        :type num_columns: int | 9
        '''

        self.nrows = num_rows
        self.ncolumns = num_columns
        self.grid = grid
        
        # Initialize variables for every cell
        self.variables = set()
        for i in range(self.nrows):
            for j in range(self.ncolumns):
                self.variables.add(Variable(i, j, self.grid[i][j] != 0))

    def output(self):
        '''
        Print sudoku
        '''
        
        print('===' * (self.ncolumns + 2))
        for i in range(self.nrows):
            if i % 3 == 0 and i != 0:
                print('||' + '---' * self.ncolumns + '--||')
            print('||', end='')
            
            for j in range(self.ncolumns):
                print(f'{self.grid[i][j] if self.grid[i][j] else " ":^3}', end='')
                if j % 3 == 2 and j != self.ncolumns - 1:
                    print('|', end='')
            print('||')
        print('===' * (self.ncolumns + 2))
        
    def neighbors(self, var):
        '''
        Find all neighbors of the variable
        
        :param var: variable
        :type var: Variable
        :return: all variables that in the same box, column or row with passed variable
        :rtype: set[Variable]
        '''
        return set(
            v for v in self.variables
            if (v.i == var.i or v.j == var.j or v.box == var.box)
            and (v != var)
        )

    @property
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, grid):
        '''
        Setter for atribute grid

        :param grid: sudoku grid
        :type grid: list[list[int]]
        :raise InvalidSudoku: when dimensions of passed grid not correspond with current object properties
        '''
        n = len(grid)
        # Check if file content match the required number of rows and columns
        if n != self.nrows or any(len(row) != self.ncolumns for row in grid):
            raise InvalidSudoku('Invalid sudoku grid')
        if not all(0 <= grid[i][j] <= n for i in range(9) for j in range(9)):
            raise InvalidSudoku('Invalid sudoku grid')
        self._grid = grid


class SudokuSolver():

    def __init__(self, sudoku: Sudoku):
        '''
        Initialize SudokuSolver

        Create initial domains for every variable with values from 1 to 9
        :type sudoku: Sudoku
        '''
        self.sudoku = sudoku
        self.domains = {
            var: {sudoku.grid[var.i][var.j]} if var.initial else 
            set(range(1, 10))
            for var in sudoku.variables
        }
        
    def grid(self, assignment):
        '''
        Generate a grid out of assignment

        :param assignment: current assignment
        :type assignment: dict[Variable, int]
        :return: filled in grid with dimentions of sudoku with None if variable is not in the assignment
        :rtype: list[list[int | None]] 
        '''
        grid = [
            [None for _ in range(self.sudoku.nrows)]
            for _ in range(self.sudoku.ncolumns)
        ]
        for var in assignment:
            grid[var.i][var.j] = assignment[var]
        return grid
        
    def print(self, assignment):
        '''
        Print an assignment
        '''
        grid = self.grid(assignment)
        print('===' * (self.sudoku.ncolumns + 2))
        for i in range(self.sudoku.nrows):
            if i % 3 == 0 and i != 0:
                print('||-' + '---' * self.sudoku.ncolumns + '-||')
            print('||', end='')
            for j in range(self.sudoku.ncolumns):
                print(f'{grid[i][j] if grid[i][j] else " ":^3}', end='')
                if j % 3 == 2 and j != self.sudoku.ncolumns - 1:
                    print('|', end='')
            print('||')
        print('===' * (self.sudoku.ncolumns + 2))
            
    def solve(self):
        '''
        Solve sudoku

        :return: a complete assignment if possible to do so
        :rtype: dict[Variable, int] | None
        '''
        
        ac3 = True
        single = True
        while ac3 or single:
            ac3 = self.ac3()
            single = self.single_possible()

        self.subsets()

        ac3 = True
        single = True
        while ac3 or single:
            ac3 = self.ac3()
            single = self.single_possible()

        assignment = {
            var: list(self.domains[var])[0] for var in self.domains 
            if len(self.domains[var]) == 1
        }

        return self.backtrack(assignment)
    
    def revise(self, x, y):
        '''
        Make variable x arc consistent with variable y
        
        :param x: first variable 
        :type x: Variable
        :param y: second variable 
        :type y: Variable
        :return: True if domain of x changed, False otherwise
        :rtype: bool
        '''
        flag = False
        
        x_vals = list(self.domains[x])
        for x_val in x_vals:
            if not any(x_val != y_val for y_val in self.domains[y]):
                flag = True
                self.domains[x].remove(x_val)
                
        return flag

    def ac3(self):
        '''
        Enforce arc consistency for every pair of variables
        
        :return: True if something changed, False otherwise
        :rtype: bool
        '''
        flag = False

        arcs = [
            (x, y) for x in self.domains 
            for y in self.sudoku.neighbors(x)
        ]

        while arcs:
            # Dequeue arcs
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False

                # Add possibly affected pairs to the queue if they not still there
                for (x, n) in [(x, n) for n in (self.sudoku.neighbors(x) - {y})]:
                    if (x, n) not in arcs:
                        arcs.append((x, n))
                flag = True

        return flag
    
    def assignment_complete(self, assignment):
        '''
        Check if assignment is complete

        :param assignment: partial or complete assignment for the sudoku
        :type assignment: dict[Variable, int]
        :return: True if assignment is complete, False otherwise
        :rtype: bool
        '''
        return set(assignment) == set(self.domains)
    
    def consistent(self, assignment):
        '''
        Check if assignment is consistent

        :param assignment: partial or complete assignment for the sudoku
        :type assignment: dict[Variable, int]
        :return: True if assignment is consistent, False otherwise
        :rtype: bool
        '''
        for var in assignment:
            neighbors = self.sudoku.neighbors(var) & set(assignment)
            for n in neighbors:
                if assignment[var] == assignment[n]:
                    return False
        return True
    
    def order_domain_values(self, var, assignment):
        '''
        Order a list of values in the domain of `var` by
        the number of values they rule out for neighboring variables.

        :param var: variable for wich domain needs to be ordered
        :type var: Variable
        :param assignment: partial assignment for the sudoku
        :type assignment: dict[Variable, int]
        :return: ordered list of values
        :rtype: list[int]
        '''
        # Find neighbors not in assignment
        neighbors = self.sudoku.neighbors(var) - set(assignment)

        # Unordered list
        vals = list(self.domains[var])
        
        # Dict that maps value to a number of ruled out values among the neighbors
        ruled_out = {}
        
        for val in vals:
            ruled_out[val] = 0
            for n in neighbors:
                for n_val in self.domains[n]:
                    if val == n_val:
                        ruled_out[val] += 1

        return sorted(vals, key=lambda val: ruled_out[val])
    
    def select_unassigned_variable(self, assignment):
        '''
        Choose an unassigned variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree

        :param assignment: partial assignment for the sudoku
        :type assignment: dict[Variable, int]
        :return: an unassigned variable
        :rtype: Variable
        '''

        # Unordered list of unassigned variables
        unassigned = list(set(self.domains) - set(assignment))

        # Sort variables according to their degree
        unassigned = sorted(unassigned, key=lambda un: len(self.sudoku.neighbors(un)), reverse=True)

        # Return sorted variables according to number of remaining values in its domain
        return sorted(unassigned, key=lambda un: len(self.domains[un]))[0]
    
    def backtrack(self, assignment):
        '''
        Backtracking Search

        :param assignment: partial or complete assignment for the sudoku
        :type assignment: dict[Variable, int]
        :return: a complete assignment if possible to do so
        :rtype: dict[Variable, int] | None
        '''

        # Check if assignment is complete
        if self.assignment_complete(assignment):
            return assignment
        
        # Select unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Loop over values of selected variable
        for val in self.order_domain_values(var, assignment):
            # Add var: value to the assignment
            assignment[var] = val 
            # Check if updated assignment is consistent
            if self.consistent(assignment):
                
                domains = self.copy_domains()
                self.domains[var] = {val}
                if result := self.solve():
                    return result
                self.domains = domains

            # Remove var from assignment
            assignment.pop(var)
        return None
    
    def single_possible(self) -> bool:
        '''
        Find if for a number only one cell possible in row, column or box
        :return: True if something changed, False otherwise
        :rtype: bool
        '''
        
        # Dict to keep track of cells
        singles = {
            'i': {i: {n: None for n in range(1, 10)} for i in range(9)},
            'j': {j: {n: None for n in range(1, 10)} for j in range(9)},
            'box': {box: {n: None for n in range(1, 10)} for box in range(9)}
        }
        flag = False

        # Loop over all variables
        for var in self.domains:
            # Loop over all values in domain
            for val in self.domains[var]:
                if val in singles['i'][var.i]:
                    # Met first time
                    if not singles['i'][var.i][val]:
                        singles['i'][var.i][val] = var
                    
                    # Met second time
                    else:
                        singles['i'][var.i].pop(val)
                    
                if val in singles['j'][var.j]:
                    if not singles['j'][var.j][val]:
                        singles['j'][var.j][val] = var
                    else:
                        singles['j'][var.j].pop(val)

                if val in singles['box'][var.box]:
                    if not singles['box'][var.box][val]:
                        singles['box'][var.box][val] = var
                    else:
                        singles['box'][var.box].pop(val)
        
        # Loop over all single possible values
        for s in singles:
            for i in singles[s]:
                for n in singles[s][i]:
                    # Check if None left -> no solution
                    if not singles[s][i][n]:
                        return False
                    if len(self.domains[singles[s][i][n]]) != 1:
                        self.domains[singles[s][i][n]] = {n}
                        flag = True

        return flag

    def subsets(self):
        '''
        Find all subsets of cells independant from their common neighbors
        '''
        
        # Set of unassigned variables
        unassigned = {var for var in self.domains if len(self.domains[var]) != 1}
        # Order according to domain length
        ordered = sorted(list(unassigned), key=lambda n: len(self.domains[n]))

        for var in ordered:
            # No solution
            if len(self.domains[var]) == 0:
                return False
            # Unassigned neighbors
            neighbors = self.sudoku.neighbors(var) & unassigned
            self.find_sub([var], neighbors)
        
        return True

    def find_sub(self, vars, common):
        '''
        Find subsets for vars and delete their values in domains of common neighbors  

        :param vars: list of variables that subset consists of
        :type vars: list[Variable]
        :param common: common neighbors of variables in list vars
        :type common: set[Variable]
        :return: True if domains changed, False otherwise
        :rtype: bool
        '''
        flag = False

        # Found subset
        if len(self.domains[vars[0]]) == len(vars):
            
            # Delete values of variables in subset from domains of their common neighbors
            for v in common:
                self.domains[v] -= self.domains[vars[0]]
            
            return True
        
        for n in common:

            # Check if variable fits subset
            if self.domains[n] <= self.domains[vars[0]]:
                vars.append(n)
                new_common = common & self.sudoku.neighbors(n)
                if new_common:
                    result = self.find_sub(vars, new_common)
                    if result:
                        flag = True
                vars.remove(n)

        return flag

    def copy_domains(self):
        return {var: set(self.domains[var]) for var in self.domains}


class InvalidSudoku(Exception):
    '''Raise for invalid sudoku grid'''