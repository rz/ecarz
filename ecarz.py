from collections import OrderedDict
import itertools


CELL_CHAR0 = ' '
CELL_CHAR1 = '*'


def rule_to_values(rule):
    binary_repr = bin(rule)[2:].rjust(8, '0')
    return binary_repr.replace('0', CELL_CHAR0).replace('1', CELL_CHAR1)


def get_new_cell_value(rule, cell, l_neighbor, r_neighbor):
    # we'll generate a dict with the different possibilities for the triplet as keys and the new cell values
    # (to represent an index of the binary representation of the rule number
    # eg rule 54 = 00110110 so, (0, 1, 1) -> 0;  (0, 1, 0) -> 1)
    # the keys are the cartesian product [char0, char1] x [char0, char1] x [char0, char1]
    states = [CELL_CHAR0, CELL_CHAR1]
    keys = sorted(itertools.product(states, states, states), reverse=True)
    values = rule_to_values(rule)
    states_map = OrderedDict(zip(keys, values))
    return states_map[(l_neighbor, cell, r_neighbor)]


def get_new_grid(rule, grid):
    # initialize if empty/None
    if not grid:
        return CELL_CHAR1.center(grid_size, CELL_CHAR0)  # one 1 cell at the middle
    new_grid = ''
    for i, (l_neighbor, cell, r_neighbor)  in enumerate(zip(CELL_CHAR0 + grid[:-1], grid, grid[1:] + CELL_CHAR0)):
        new_grid += get_new_cell_value(rule, cell, l_neighbor, r_neighbor)
    return new_grid

if __name__ == '__main__':
    # todo: make these command line opts
    rule = 90  # Wolfram convention: http://mathworld.wolfram.com/ElementaryCellularAutomaton.html
    grid_size = 101
    max_steps = 50
    grid = None

    # evolve the automaton for the given number of steps
    for _ in range(max_steps):
        # the funny arguments in the zip are to get the boundary condition:
        # for now, start with "blank cell" boundary conditions ie always assume there is a blank
        # cell to the left and right of the grid's ends
       grid = get_new_grid(rule, grid)
       print(grid)
