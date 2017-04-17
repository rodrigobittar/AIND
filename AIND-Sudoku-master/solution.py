
rows = 'ABCDEFGHI'
cols = '123456789'

digits = cols


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + t for s in A for t in B]

row_units = [cross(r, cols) for r in rows]

colum_units = [cross(rows, c) for c in cols]

square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

diagonals = [[ rows[i] + cols[i] for i in range(len(rows)) ], [ rows[len(rows)-1-i] + cols[i] for i in range(len(rows)) ]] 

unitlist = row_units + colum_units + square_units + diagonals 

boxes = cross(rows, cols) # every box

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes) 

assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Select all box with two possibilities
    Value2Box = [ box for box in boxes if len(values[box])==2 ]
    for box in Value2Box:
        digitS = values[box]
        # Extract all present naked twins for this box 
        nakedTwins = [ peer for peer in peers[box] if peer in Value2Box and values[peer] == digitS]
        for nakedTwin in nakedTwins:
            # common peers
            commonPeers = [ peer for peer in peers[box] if peer in peers[nakedTwin] ]
            for commonPeer in commonPeers:
                # Remove the digits of the naked twins
                assign_value(values, commonPeer, ''.join( [ d for d in values[commonPeer] if d not in digitS ] ))
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = [ (digits if c == '.' else c) for c in grid ]
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return
    pass

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solves_values = [ box for box in values.keys() if len(values[box])==1 ]
    for box in solves_values:
        digit = values[box] 
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, ''))
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in digits:
            boxesC = [box for box in unit if digit in values[box]]
            if len(boxesC) == 1:
                
                assign_value(values, boxesC[0], digit)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy and the Only Choice Strategy
        values = only_choice(eliminate(naked_twins(values)))
        
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    values = reduce_puzzle(values)
    if values is False:
        return False 

    if all(len(values[box])==1 for box in boxes):
        return values 

    # We take the one of the squares without filling with less possibilities
    num, minBox = min((len(values[box]), box) for box in boxes if len(values[box])>1)
    
    for digit in values[minBox]:
        copySudoku = values.copy()
        copySudoku[minBox] = digit
        possibleSudoku = search(copySudoku)
        if possibleSudoku:
            return possibleSudoku 

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
