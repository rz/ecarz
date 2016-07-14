import argparse
import collections


def handle_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-d', '--dimension', help='The dimension of the automaton. Only 1d and 2d automata are supported',
            type=int, default=1)
    parser.add_argument(
            '-r', '--rule', help='Rule number (according to the Wolfram convention) of the automaton to simulate',
            type=int, required=True)
    parser.add_argument(
            '-g', '--grid-size', help='Number of cells in the grid in 1d. In 2d the grid will be a grid-size x grid-size square.',
            type=int, default=101)
    parser.add_argument(
            '-s', '--steps', help='Number of steps to simulate the automaton for',
            type=int, default=50)
    parser.add_argument(
            '-G', '--grid', help='The initial state of the grid. Only supported in 1d, ignored if --dimension is 2. Specifying this option overrides the grid-size option. By default, an empty cell is represented by a single space character and a filled cell by *, but this can be changed with the --char-zero and --char-one options.',
            type=str, default=None)
    parser.add_argument(
            '--char-zero', help='The character to use for a cell in state 0 in human-friendly representations. Default is a space.',
            type=str, default=' ')
    parser.add_argument(
            '--char-one', help='The character to use for a cell in state 1 in human-friendly representations. Default is *.',
            type=str, default='*')

    args = parser.parse_args()

    if args.grid is not None and args.dimension == 1:
        grid_size = len(args.grid)
        grid_str = args.grid
    else:
        grid_size = args.grid_size
        grid_str = None
    return args.dimension, args.rule, grid_str, grid_size, args.steps, args.char_zero, args.char_one


class Grid(collections.UserList):
    def __init__(self, dimension, size, char0=' ', char1='*'):
        self.char0, self.char1 = char0, char1
        if dimension not in [1, 2]:
            raise ValueError('Only 1d and 2d grids are supported.')

        self.dimension = dimension
        self.size = size

        middle_row = [int(c) for c in '1'.center(size, '0')]  # one 1 cell at the middle. hacky, but the center() method is handy
        if dimension == 1:
            self.data = middle_row
        else:
            self.data = [[0 for _ in range(size)] for _ in range(size - 1)]
            self.data.insert(size//2, middle_row)

    def __str__(self):
        if self.dimension == 1:
            return ''.join(str(i) for i in self.data).replace('0', self.char0).replace('1', self.char1)
        else:
            raise NotImplemented

    def get_neighbor_tuples(self):
        if self.dimension == 1:
            return zip([0] + grid[:-1], grid, grid[1:] + [0])
        else:
            raise NotImplemented

    def set_state(self, state):
        self.data = state


def parse_grid(grid_str, char0, char1):
    return [int(c) for c in grid_str.replace(char0, '0').replace(char1, '1')]


def get_next_cell_state(rule, cells):
    # the rule numbers follow the Wolfram convention, so we'll need the binary
    # representation of the given number and we'll use the 3 cells as an index
    # into that representation.
    # eg rule 54 is 00110110 (54 in binary) so, (0, 0, 0) -> 0;  (0, 0 ,1) -> 1, (0, 1, 0) -> 1, ...)
    # see http://mathworld.wolfram.com/ElementaryCellularAutomaton.html for more detail
    binary_rule_repr = bin(rule)[2:].rjust(8, '0')
    next_states = [int(c) for c in binary_rule_repr]
    index = sum(i * j for i, j in zip(cells, (4, 2, 1)))  # this is converting a triplet of zeros and ones to base 10 eg (1, 1, 0) -> 6
    return next_states[index]


def get_next_grid_state(rule, grid):
    # the funny arguments in the zip are to get the boundary condition:
    # we use "blank cell" boundary conditions ie always assume there is a blank
    # cell to the left and right of the grid's ends.
    # todo: support other types of boundary conditions?
    cells = grid.get_neighbor_tuples()
    new_grid = Grid(grid.dimension, grid.size, grid.char0, grid.char1)
    new_grid.set_state([get_next_cell_state(rule, (l, c, r)) for l, c, r in cells])
    return new_grid


if __name__ == '__main__':
    dimension, rule, grid_str, grid_size, max_steps, char0, char1 = handle_args()
    grid = Grid(dimension, grid_size, char0=char0, char1=char1)
    if dimension == 1 and grid_str is not None:
        grid.set_state(parse_grid(grid_str, char0, char1))
    print(grid)

    # evolve the automaton for the given number of steps and print each one
    for _ in range(max_steps):
        grid = get_next_grid_state(rule, grid)
        print(grid)

