import pandas as pd
import numpy as np
import os


class soduku:

    def __init__(self, soduku_file_path, separator=" "):

        # Generate the full path from root to the soduku solver, load it via numpy
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), soduku_file_path)
        self.__original_grid = np.loadtxt(full_path, dtype=np.int)
        self.__solver_grid = np.copy(self.__original_grid)
        self.__solved = False
        self.possible_values = [[None for i in range(9)] for j in range(9)]

    def print_invalid(self):
        print("Invalid grid generated!")
        self.print()

    def valid_grid(self):
        
        # Check all rows, columns and boxes for duplicates. As soon as one is found, return false, else true
        # Row check
        for row in self.__solver_grid:
            _, counts = np.unique(row[row>0], return_counts=True)
            if np.any(counts>1):
                self.print_invalid()
                return False

        # Column check
        for col in self.__solver_grid.T:
            _, counts = np.unique(col[col>0], return_counts=True)
            if np.any(counts>1):
                self.print_invalid()
                return False

        # Box check
        for row_index in range(3):
            for col_index in range(3):
                box = self.__solver_grid[row_index*3:(row_index+1)*3, col_index*3:(col_index+1)*3]
                flattened = box.flatten()
                _, counts = np.unique(flattened[flattened>0], return_counts=True)
                if np.any(counts>1):
                    self.print_invalid()
                    return False

        # If all rows, columns and boxes are OK, grid is valid
        return True

    def get_box(self, row, col):

        if row < 3 and col<3:
            return_arr =  self.__solver_grid[:3, :3]
        elif row<3 and col<6:
            return_arr =  self.__solver_grid[:3, 3:6]
        elif row<3 and col<9:
            return_arr =  self.__solver_grid[:3, 6:9]
        elif row<6 and col<3:
            return_arr =  self.__solver_grid[3:6, :3]
        elif row<6 and col<6:
            return_arr =  self.__solver_grid[3:6, 3:6]
        elif row<6 and col<9:
            return_arr =  self.__solver_grid[3:6, 6:9]
        elif row<9 and col<3:
            return_arr =  self.__solver_grid[6:9, :3]
        elif row<9 and col<6:
            return_arr =  self.__solver_grid[6:9, 3:6]
        else:
            return_arr =  self.__solver_grid[6:9, 6:9]

        return return_arr.flatten()

    
    # Function to get the values that are implicitly blocked, 
    def get_blocked(self,row, col, rows, cols, rows_loop, cols_loop):
        col_blocked = set()
        row_blocked = set()
       
        for col_block in cols:
            if self.possible_values[row][col_block] is not None:
                col_blocked = col_blocked.union(set(self.possible_values[row][col_block]))
                for row_block in rows_loop:
                    if self.possible_values[row_block][col_block] is not None:
                        col_blocked -= set(self.possible_values[row_block][col_block])

        for row_block in rows:
            if self.possible_values[row_block][col] is not None:
                row_blocked = row_blocked.union(set(self.possible_values[row_block][col]))
                for col_block in cols_loop:
                    if self.possible_values[row_block][col_block] is not None:
                        row_blocked -= set(self.possible_values[row_block][col_block])

        return col_blocked.union(row_blocked)

    def get_blocked_possible(self, row, col):

        three = set([0,1,2])
        six = set([3,4,5])
        nine = set([6,7,8])

        if row < 3 and col<3:

            rows_loop = three-set([row]) #Rader att "ta bort" vid kolumnloop
            cols_loop = three-set([col]) #Kolumner att ta bot vid rad-loop
            cols = six.union(nine) # Totala kolumner att loopa över
            rows = six.union(nine) # Totala rader att loopa över

            return self.get_blocked(row, col, rows, cols, rows_loop, cols_loop)

        elif row<3 and col<6:
            rows_loop = three-set([row])
            cols_loop = six-set([col])
            cols = three.union(nine)
            rows = six.union(nine)

            return self.get_blocked(row, col, rows, cols, rows_loop, cols_loop)

        elif row<3 and col<9:
            rows_loop = three-set([row])
            cols_loop = nine-set([col])
            cols = six.union(three)
            rows = six.union(nine)

            return self.get_blocked(row, col, rows, cols, rows_loop, cols_loop)

        elif row<6 and col<3:
            rows_loop = six-set([row])
            cols_loop = three-set([col])
            cols = six.union(nine)
            rows = three.union(nine)

            return self.get_blocked(row, col, rows, cols, rows_loop, cols_loop)
            
        elif row<6 and col<6:
            rows_loop = six-set([row])
            cols_loop = six-set([col])
            cols = three.union(nine)
            rows = three.union(nine)

            return self.get_blocked(row, col, rows, cols, rows_loop, cols_loop)
            
        elif row<6 and col<9:
            rows_loop = six-set([row])
            cols_loop = nine-set([col])
            cols = six.union(three)
            rows = three.union(nine)

            return self.get_blocked(row, col, rows, cols, rows_loop, cols_loop)
            
        elif row<9 and col<3:
            rows_loop = nine-set([row])
            cols_loop = three-set([col])
            cols = six.union(nine)
            rows = six.union(three)

            return self.get_blocked(row, col, rows, cols, rows_loop, cols_loop)
            
        elif row<9 and col<6:
            rows_loop = nine-set([row])
            cols_loop = six-set([col])
            cols = three.union(nine)
            rows = six.union(three)

            return self.get_blocked(row, col, rows, cols, rows_loop, cols_loop)
            
        else:
            rows_loop = nine-set([row])
            cols_loop = nine-set([col])
            cols = six.union(three)
            rows = six.union(three)

            return self.get_blocked(row, col, rows, cols, rows_loop, cols_loop)
            

    def solve(self):

        possible_values = set(range(1, 10))
        first = True
    
        while not self.__solved:
            added = False

            for row in range(9):
                for col in range(9):

                    if self.__solver_grid[row, col] == 0:
                        whole_row = self.__solver_grid[row, :]
                        whole_col = self.__solver_grid[:, col]
                        whole_box = self.get_box(row, col)

                        blocked_possible = self.get_blocked_possible(row, col)

                        # Check what numbers that are blocked either by current row, column or box. 
                        if len(blocked_possible) == 0:
                            block_values = set(np.concatenate((whole_row[whole_row>0], whole_col[whole_col>0], whole_box[whole_box>0])))
                        else:
                            block_values = set(np.concatenate((whole_row[whole_row>0], whole_col[whole_col>0], whole_box[whole_box>0], np.array(list(blocked_possible)))))
                        available_values = possible_values-block_values
                        self.possible_values[row][col] = list(available_values)
                        if len(available_values) == 1:
                            added = True 
                            self.__solver_grid[row, col] = available_values.pop()

            # Lägg till att kolla om det endast är en tom i rad/kolumn/box. Se till att self.possible_values uppdateras. Försök skriva om get_blocked_possible
            if not self.valid_grid():
                print("Invalid grid!")
            else:
                print("Grid OK!")

            if 0 not in self.__solver_grid.flatten():
                print("Sudoku solved!")
                self.print()
                self.__solved = True

            if not added and not first:
                print("Solver stuck!")
                self.print()
                print(len(self.possible_values))
                for row in self.possible_values:
                    print(row)
                break
            first = False

    def print(self):
        print(self.__solver_grid)

        

soduku = soduku("soduku5.txt")
soduku.solve()