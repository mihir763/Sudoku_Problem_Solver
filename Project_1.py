#!/usr/bin/env python
# coding: utf-8

# # Sudoku Solver 

# Steps to solve the Sudoku problem:  
# Step 1: Define the Linear Programming problem  
# Step 2: Set the objective function  
# Step 3: Define the decision variables  
# Step 4: Set the constraints  
# Step 5: Solve the Sudoku puzzle  
# Step 6: Check if an optimal result is found
# Step 7: Print the result

# ## NORMAL & DIAGONAL SUDOKU

# In[1]:


import pulp as plp


# ## Add constraints

# ### Default Constraints

# In[2]:


def add_default_sudoku_constraints(prob, grid_vars, rows, cols, grids, values):
    
    # Constraint to ensure only one value is filled for a cell
    for row in rows:
        for col in cols:
                prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[row][col][value] for value in values]),
                                        sense=plp.LpConstraintEQ, rhs=1, name=f"constraint_sum_{row}_{col}"))


    # Constraint to ensure that values from 1 to 9 is filled only once in a row        
    for row in rows:
        for value in values:
            prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[row][col][value]*value  for col in cols]),
                                        sense=plp.LpConstraintEQ, rhs=value, name=f"constraint_uniq_row_{row}_{value}"))

    # Constraint to ensure that values from 1 to 9 is filled only once in a column        
    for col in cols:
        for value in values:
            prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[row][col][value]*value  for row in rows]),
                                        sense=plp.LpConstraintEQ, rhs=value, name=f"constraint_uniq_col_{col}_{value}"))


    # Constraint to ensure that values from 1 to 9 is filled only once in the 3x3 grid       
    for grid in grids:
        grid_row  = int(grid/3)
        grid_col  = int(grid%3)

        for value in values:
            prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[grid_row*3+row][grid_col*3+col][value]*value  for col in range(0,3) for row in range(0,3)]),
                                        sense=plp.LpConstraintEQ, rhs=value, name=f"constraint_uniq_grid_{grid}_{value}"))


# ### Add the diagonal constraints

# Constraint 5: Each diagonal should contain every number from 1 to 9 once

# In[3]:


def add_diagonal_sudoku_constraints(prob, grid_vars, rows, cols, values):
    
        # Constraint from top-left to bottom-right - numbers 1 - 9 should not repeat
        for value in values:
                prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[row][row][value]*value  for row in rows]),
                                            sense=plp.LpConstraintEQ, rhs=value, name=f"constraint_uniq_diag1_{value}"))


        # Constraint from top-right to bottom-left - numbers 1 - 9 should not repeat
        for value in values:
                prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[row][len(rows)-row-1][value]*value  for row in rows]),
                                            sense=plp.LpConstraintEQ, rhs=value, name=f"constraint_uniq_diag2_{value}"))


# ### Add the prefilled values as constraints

# Constraint 6: Fill the prefilled cells as constraints to the LP problem.

# In[4]:


def add_prefilled_constraints(prob, input_sudoku, grid_vars, rows, cols, values):
    for row in rows:
        for col in cols:
            if(input_sudoku[row][col] != 0):
                prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[row][col][value]*value  for value in values]), 
                                                    sense=plp.LpConstraintEQ, 
                                                    rhs=input_sudoku[row][col],
                                                    name=f"constraint_prefilled_{row}_{col}"))


# ## Extract & Print Solution

# ### Extract solution from the target variable to a list array

# In[5]:


def extract_solution(grid_vars, rows, cols, values):
    solution = [[0 for col in cols] for row in rows]
    grid_list = []
    for row in rows:
        for col in cols:
            for value in values:
                if plp.value(grid_vars[row][col][value]):
                    solution[row][col] = value 
    return solution


# ### Print the solution as a Sudoku grid

# In[6]:


def print_solution(solution, rows,cols):
    # Print the final result
    print(f"\nFinal result:")

    print("\n\n+ ----------- ++ ----------- ++ ----------- ++",end="")
    for row in rows:
        print("\n",end="\n|  ")
        for col in cols:
            num_end = "  |  " if ((col+1)%3 == 0) else "   "
            print(solution[row][col],end=num_end)

        if ((row+1)%3 == 0):
            print("\n\n+ ----------- ++ ----------- ++ ----------- ++",end="")


# ## Sudoku Solver

# Sudoku Solver: Find a solution where the constraints are satisfied.   
# Need to identify a feasible solution and not an optimal solution.
# 
# Decision Variables: 9x9x9 --> Binary variables: (row,column, value)   
# Create a set of binary variables. 9 binary variables for each cell (row,col) - one for each value from 1 to 9.  
# For every cell, only one of the 9 binary variables for that (row,col) can be set (constraint)

# In[7]:


def solve_sudoku(input_sudoku, diagonal = False ):
    # Create the linear programming problem
    prob = plp.LpProblem("Sudoku_Solver")

    rows = range(0,9)
    cols = range(0,9)
    grids = range(0,9)
    values = range(1,10)

    # Decision Variable/Target variable
    grid_vars = plp.LpVariable.dicts("grid_value", (rows,cols,values), cat='Binary') 

    # Set the objective function
    # Sudoku works only on the constraints - feasibility problem 
    # There is no objective function that we are trying maximize or minimize.
    # Set a dummy objective
    objective = plp.lpSum(0)
    prob.setObjective(objective)

    # Create the default constraints to solve sudoku
    add_default_sudoku_constraints(prob, grid_vars, rows, cols, grids, values)

    # Add the diagonal constraints if flag is set
    if (diagonal):
        add_diagonal_sudoku_constraints(prob, grid_vars, rows, cols, values)
        
    # Fill the prefilled values from input sudoku as constraints
    add_prefilled_constraints(prob, input_sudoku, grid_vars, rows, cols, values)


    # Solve the problem
    prob.solve()

    # Print the status of the solution
    solution_status = plp.LpStatus[prob.status]
    print(f'Solution Status = {plp.LpStatus[prob.status]}')

    # Extract the solution if an optimal solution has been identified
    if solution_status == 'Optimal':
        solution = extract_solution(grid_vars, rows, cols, values)
        print_solution(solution, rows,cols)


            


# ## Run the Normal Sudoku

# In[8]:


normal_sudoku = [
                    [3,0,0,8,0,0,0,0,1],
                    [0,0,0,0,0,2,0,0,0],
                    [0,4,1,5,0,0,8,3,0],
                    [0,2,0,0,0,1,0,0,0],
                    [8,5,0,4,0,3,0,1,7],
    
                    [0,0,0,7,0,0,0,2,0],
                    [0,8,5,0,0,9,7,4,0],
                    [0,0,0,1,0,0,0,0,0],
                    [9,0,0,0,0,7,0,0,6]
                ]


solve_sudoku(input_sudoku=normal_sudoku, diagonal=False)


# 

# In[ ]:




