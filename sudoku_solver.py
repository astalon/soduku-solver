import pandas as pd
import numpy as np
import os
from collections import Counter
import time
import cProfile
import pstats
import io
import itertools

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

    # Function to update effect of naked pairs in box
    def naked_pairs_box(self, row, col):

        naked_pair = None
        box_possible = self.get_box_possible(row, col)
        original = box_possible.to_numpy().flatten().tolist()
        flattened = [val for val in original if val is not None and len(val)==2]

        df = pd.DataFrame(flattened)
        ret = df.value_counts()

        for index, val in ret.iteritems():
            if val == 2:
                naked_pair = list(index)

        if naked_pair is not None:
            for index_row, row_possible in box_possible.iterrows():
                for index_col, possible in row_possible.iteritems():
                    if possible is not None:
                        if possible != naked_pair:
                            self.possible_values.iat[index_row, index_col] = list(set(self.possible_values.iloc[index_row, index_col])-set(naked_pair))


    # Get implicit blocks for column
    def naked_pairs_col(self, col):

        naked_pair = None
        col_possible = self.possible_values.iloc[:, col]
        flattened = [val for val in list(col_possible) if val is not None and len(val)==2]

        df = pd.DataFrame(flattened)
        ret = df.value_counts()

        for index, val in ret.iteritems():
            if val == 2:
                naked_pair = list(index)

        if naked_pair is not None:
            for index_row, val in col_possible.iteritems():
                if val is not None:
                    if val != naked_pair:
                        self.possible_values.iat[index_row, col] = list(set(self.possible_values.iloc[index_row, col])-set(naked_pair))


    # Get implicit blocks for row
    def naked_pairs_row(self, row):
        naked_pair = None
        row_possible = self.possible_values.iloc[row, :]
        flattened = [val for val in list(row_possible) if val is not None and len(val)==2]

        df = pd.DataFrame(flattened)
        ret = df.value_counts()

        for index, val in ret.iteritems():
            if val == 2:
                naked_pair = list(index)

        if naked_pair is not None:
            for index_col, val in row_possible.iteritems():
                if val is not None:
                    if val != naked_pair:
                        self.possible_values.iat[row, index_col] = list(set(self.possible_values.iloc[row, index_col])-set(naked_pair))

    # Obtain the possible values in a cell given its row and column, direct deducting
    def get_possible(self, row, col):

        possible_values = set(range(1, 10))

        whole_row = self.__solver_grid[row, :]
        whole_col = self.__solver_grid[:, col]
        whole_box = self.get_box(row, col)

        available = possible_values - set(np.concatenate((whole_row[whole_row>0], whole_col[whole_col>0], whole_box[whole_box>0])))

        return list(available)

    # Update all values in the grid with their possible values
    def update_possible(self):

        for row in range(9):
            for col in range(9):
                
                if self.__solver_grid[row, col] == 0:
                    self.possible_values.iat[row, col] = self.get_possible(row, col)
                else:
                    self.possible_values.iloc[row, col] = None

        for row in range(0, 9 , 3):
            for col in range(0, 9, 3):
                self.naked_pairs_box(row, col)

        for i in range(9):
            self.naked_pairs_row(i)
            self.naked_pairs_col(i)

        for row in range(9):
            self.hidden_subsets_row(row)


    # Räkna hur många gånger de olika kombinationerna förekommer på andra "possible" ställen, om endast två, ta bort alla andra possibles
    def hidden_subsets_row(self, row):
        
        row_possible = self.possible_values.iloc[row, :]

        for col, possible in row_possible.iteritems():
            if possible is not None:
                combinations = itertools.combinations(possible, 2)
                print(list(combinations))
                exit(1)



    def solve(self):

        while not self.__solved:

            added = False

            for row in range(9):
                for col in range(9):
                    if self.__solver_grid[row, col] == 0:

                        available_values = self.get_possible(row, col)

                        # If it is only one possible digit in cell, put it there right away
                        if len(available_values) == 1:
                            self.__solver_grid[row, col] = available_values.pop()
                            self.possible_values.iloc[row, col] = None
                            added = True
            update=True
            if not added:
                for row in range(9):
                    for col in range(9):

                        if self.__solver_grid[row, col] == 0:
                            if update:
                                self.update_possible()
                                update=False

                            single_possible = set(self.possible_values.iloc[row, col])

                            if len(single_possible) == 1:
                                self.__solver_grid[row, col] = single_possible.pop()
                                self.possible_values.iloc[row, col] = None
                                update = True
                                added = True
                            else:

                                # Sole candidate in a column?
                                if not added:
                                    sole_possible_col = set(self.possible_values.iloc[row, col])
                                    col_possible = self.possible_values.iloc[:, col]
                                    for ix_row, val in col_possible.iteritems():
                                        if ix_row == row:
                                            pass
                                        elif val is not None:
                                            sole_possible_col = sole_possible_col - set(val)
                                    
                                    if len(sole_possible_col) == 1:
                                        self.__solver_grid[row, col] = sole_possible_col.pop()
                                        update = True
                                        added = True

                                # Sole candidate in a box?
                                if not added:
                                    box_possible = self.get_box_possible(row,col)
                                    for index_row, row_possible in box_possible.iterrows():
                                        for index_col, col_possible in row_possible.iteritems():
                                            if col_possible is not None:
                                                if index_row == row and index_col == col:
                                                    pass
                                                else:
                                                    single_possible = single_possible - set(col_possible)

                                    single_possible = single_possible - self.get_blocked_implicit(row, col)
                                    if len(single_possible) == 1:
                                        self.__solver_grid[row, col] = single_possible.pop()
                                        self.possible_values.iloc[row, col] = None
                                        update=True
                                        added = True

                                # Sole candidate in row?
                                if not added:
                                    sole_possible_row = set(self.possible_values.iloc[row, col])
                                    row_possible = self.possible_values.iloc[row, :]
                                    for ix_col, val in row_possible.iteritems():
                                        if ix_col == col:
                                            pass
                                        elif val is not None:
                                            sole_possible_row = sole_possible_row - set(val)
                                    
                                    if len(sole_possible_row) == 1:
                                        self.__solver_grid[row, col] = sole_possible_row.pop()
                                        added = True                           


            if not self.valid_grid():
                print("Invalid grid!")
                exit(1)
            else:
                print("Grid OK!")

            if 0 not in self.__solver_grid.flatten():
                print("Sudoku solved!")
                if not self.valid_grid():
                    print("Invalid grid!")
                    exit(1)
                else:
                    print("Grid OK!")

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


pr = cProfile.Profile()
pr.enable()

soduku = soduku("soduku4.txt")
soduku.solve()

pr.disable()
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumtime')
ps.print_stats()

full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "profile.txt")
with open(full_path, 'w+') as f:
    f.write(s.getvalue())