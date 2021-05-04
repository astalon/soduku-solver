import pandas as pd
import numpy as np
import os
from collections import Counter


class soduku:

    def __init__(self, soduku_file_path, separator=" "):

        # Generate the full path from root to the soduku solver, load it via numpy
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), soduku_file_path)
        self.__original_grid = np.loadtxt(full_path, dtype=np.int)
        self.__solver_grid = np.copy(self.__original_grid)
        self.__solved = False
        self.possible_values = pd.DataFrame(np.zeros((9,9)))
        self.possible_values.iloc[:, :] = None

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

    # return the "current box" of possible values from current row and column
    def get_box_possible(self, row, col):

        if row < 3 and col<3:
            return_box =  self.possible_values.iloc[:3, :3]
        elif row<3 and col<6:
            return_box =  self.possible_values.iloc[:3, 3:6]
        elif row<3 and col<9:
            return_box =  self.possible_values.iloc[:3, 6:9]
        elif row<6 and col<3:
            return_box =  self.possible_values.iloc[3:6, :3]
        elif row<6 and col<6:
            return_box =  self.possible_values.iloc[3:6, 3:6]
        elif row<6 and col<9:
            return_box =  self.possible_values.iloc[3:6, 6:9]
        elif row<9 and col<3:
            return_box =  self.possible_values.iloc[6:9, :3]
        elif row<9 and col<6:
            return_box =  self.possible_values.iloc[6:9, 3:6]
        else:
            return_box =  self.possible_values.iloc[6:9, 6:9]

        return return_box

    
    # Function to get the values that are implicitly blocked
    def get_blocked(self,current_row, current_col, col_box_1, col_box_2, rows_loop, row_box_1, row_box_2, cols_loop):
        box1_blocked = set()
        box2_blocked = set()

        box3_blocked = set()
        box4_blocked = set()

        # Values that are blocked implicitly from neighboring columns
        for col in col_box_1:
            val = self.possible_values.iloc[current_row,col]
            if val is not None:
                box1_blocked = box1_blocked.union(val)

        for col in col_box_1:
            for row in rows_loop:
                val = self.possible_values.iloc[row, col]
                if val is not None:
                    box1_blocked = box1_blocked - set(val)

        for col in col_box_2:
            val = self.possible_values.iloc[current_row,col]
            if val is not None:
                box2_blocked = box2_blocked.union(val)

        for col in col_box_2:
            for row in rows_loop:
                val = self.possible_values.iloc[row, col]
                if val is not None:
                    box2_blocked = box2_blocked - set(val)

        # Values that are blocked implicitly from neighboring rows
        for row in row_box_1:
            val = self.possible_values.iloc[row,current_col]
            if val is not None:
                box3_blocked = box3_blocked.union(val)

        for row in row_box_1:
            for col in cols_loop:
                val = self.possible_values.iloc[row, col]
                if val is not None:
                    box3_blocked = box3_blocked - set(val)

        for row in row_box_2:
            val = self.possible_values.iloc[row,current_col]
            if val is not None:
                box4_blocked = box4_blocked.union(val)

        for row in row_box_2:
            for col in cols_loop:
                val = self.possible_values.iloc[row, col]
                if val is not None:
                    box4_blocked = box4_blocked - set(val)

        # We are interested in the union of the blocked values
        return set()


    def get_blocked_implicit(self, row, col):

        three = set([0,1,2])
        six = set([3,4,5])
        nine = set([6,7,8])

        if row < 3 and col<3:

            rows_loop = three-set([row]) #Rader att "ta bort" vid kolumnloop
            box1 = six
            box2 = nine

            cols_loop = three-set([col])
            box3 = six
            box4 = nine

        elif row<3 and col<6:
            rows_loop = three-set([row])
            box1 = three
            box2 = nine

            cols_loop = six-set([col])
            box3 = six
            box4 = nine

        elif row<3 and col<9:
            rows_loop = three-set([row])
            box1 = three
            box2 = six

            cols_loop = nine-set([col])
            box3 = six
            box4 = nine

        elif row<6 and col<3:
            rows_loop = six-set([row])
            box1 = six
            box2 = nine

            cols_loop = three-set([col])
            box3 = three
            box4 = nine
            
        elif row<6 and col<6:
            rows_loop = six-set([row])
            box1 = three
            box2 = nine

            cols_loop = six-set([col])
            box3 = three
            box4 = nine
            
        elif row<6 and col<9:
            rows_loop = six-set([row])
            box1 = three
            box2 = six

            cols_loop = nine-set([col])
            box3 = three
            box4 = nine
            
        elif row<9 and col<3:
            rows_loop = nine-set([row])
            box1 = six
            box2 = nine
            
            cols_loop = three-set([col])
            box3 = three
            box4 = six

        elif row<9 and col<6:
            rows_loop = nine-set([row])
            box1 = three
            box2 = nine

            cols_loop = six-set([col])
            box3 = three
            box4 = six

        else:
            rows_loop = nine-set([row])
            box1 = three
            box2 = six

            cols_loop = nine-set([col])
            box3 = three
            box4 = six

        return self.get_blocked(row, col,box1, box2, rows_loop, box3, box4, cols_loop)


    def get_possible(self, row, col):

        possible_values = set(range(1, 10))

        whole_row = self.__solver_grid[row, :]
        whole_col = self.__solver_grid[:, col]
        whole_box = self.get_box(row, col)

        available = possible_values - set(np.concatenate((whole_row[whole_row>0], whole_col[whole_col>0], whole_box[whole_box>0])))
        if available == set([]):
            print(self.__solver_grid)
            print(row, col)
            exit(1)

        return list(available)


    def update_possible(self):

        for row in range(9):
            for col in range(9):
                
                if self.__solver_grid[row, col] == 0:
                    self.possible_values.iat[row, col] = self.get_possible(row, col)
                else:
                    self.possible_values.iloc[row, col] = None

    def solve(self):

        possible_values = set(range(1, 10))
        last_added_row = 10
        last_added_col = 10
        while not self.__solved:

            added = False

            for row in range(9):
                for col in range(9):

                    if self.__solver_grid[row, col] == 0:
                        whole_row = self.__solver_grid[row, :]
                        whole_col = self.__solver_grid[:, col]
                        whole_box = self.get_box(row, col)

                        block_values =  set(np.concatenate((whole_row[whole_row>0], whole_col[whole_col>0], whole_box[whole_box>0])))
                        available_values = possible_values-block_values

                        # If it is only one possible digit in cell, put it there right away
                        if len(available_values) == 1:

                            self.__solver_grid[row, col] = available_values.pop()
                            self.possible_values.iloc[row, col] = None
                            added = True
                            last_added_row = row
                            last_added_col = col

            if not added:
                for row in range(9):
                    for col in range(9):

                        if self.__solver_grid[row, col] == 0:
                            self.update_possible()

                            box_possible = self.get_box_possible(row,col)

                            single_possible = set(self.possible_values.iloc[row, col])

                            for index_row, row_possible in box_possible.iterrows():
                                for index_col, col_possible in row_possible.iteritems():
                                    if col_possible is not None:
                                        if index_row != row and index_col != col:
                                            single_possible = single_possible - set(col_possible)

                            if len(single_possible) == 1:
                                self.__solver_grid[row, col] = single_possible.pop()
                                self.possible_values.iloc[row, col] = None
                                added = True
                                last_added_row = row
                                last_added_col = col

                            # else:
                            #     implicit_block = self.get_blocked_implicit(row, col)

                            #     if len(implicit_block) > 0:
                            #         available_values = available_values - implicit_block

                            #         if len(available_values) == 1:
                            #             self.__solver_grid[row, col] = available_values.pop()
                            #             self.possible_values.iloc[row, col] = None
                            #             added = True

            if not self.valid_grid():
                print("Invalid grid!")
                exit(1)
            else:
                print("Grid OK!")

            if 0 not in self.__solver_grid.flatten():
                print("Sudoku solved!")
                self.print()
                self.__solved = True

            if not added:

                u, counts = np.unique(self.__solver_grid.flatten(), return_counts=True)
                print("Solver stuck!")
                print("Numbers solved: ", 81-counts[0])
                self.print()
                print(self.possible_values)
                break


    def print(self):
        print(self.__original_grid)
        print(self.__solver_grid)

        

soduku = soduku("soduku5.txt")
soduku.solve()