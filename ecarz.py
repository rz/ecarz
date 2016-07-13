import argparse
from collections import OrderedDict
import itertools


#if these change, change the help for the -G flag in parse_args()  # todo: make it so that these can be changed in one place
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


def initialize_grid():
    return CELL_CHAR1.center(grid_size, CELL_CHAR0)  # one 1 cell at the middle


def get_new_grid(rule, grid):
    # the funny arguments in the zip are to get the boundary condition:
    # for now, start with "blank cell" boundary conditions ie always assume there is a blank
    # cell to the left and right of the grid's ends
    new_grid = ''
    for i, (l_neighbor, cell, r_neighbor)  in enumerate(zip(CELL_CHAR0 + grid[:-1], grid, grid[1:] + CELL_CHAR0)):
        new_grid += get_new_cell_value(rule, cell, l_neighbor, r_neighbor)
    return new_grid


def handle_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-r', '--rule', help='Rule number (according to the Wolfram convention) of the automaton to simulate',
            type=int, required=True)
    parser.add_argument(
            '-g', '--grid-size', help='Number of cells in the grid',
            type=int, default=101)
    parser.add_argument(
            '-s', '--steps', help='Number of steps to simulate the automaton for',
            type=int, default=50)
    parser.add_argument(
            '-G', '--grid', help='The initial state of the grid. Specifying this option overrides the grid-size option. An empty cell is represented by a single space character and a filled cell by *.',
            type=str, default=None)

    args = parser.parse_args()
    if args.grid is None:
        return args.rule, args.grid, args.grid_size, args.steps
    else:
        return args.rule, args.grid, len(args.grid), args.steps

if __name__ == '__main__':
    rule, grid, grid_size, max_steps = handle_args()

    # initial step
    if grid is None:
        grid = initialize_grid()
    print(grid)

    # evolve the automaton for the given number of steps and print each one
    for _ in range(max_steps):
      grid = get_new_grid(rule, grid)
      print(grid)

