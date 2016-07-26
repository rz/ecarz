import argparse
import collections
import random
import time


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
            formatted = ''.join(str(i) for i in self)
        else:
            formatted = '\n'.join(''.join(str(i) for i in l) for l in self)
        return formatted.replace('0', self.char0).replace('1', self.char1)

    def get_neighbor_tuples(self):
        if self.dimension == 1:
            # the funny arguments in the zip are to get the boundary condition:
            # we use "blank cell" boundary conditions ie always assume there is a blank
            # cell to the left and right of the grid's ends.
            # todo: support other types of boundary conditions?
            return zip([0] + self[:-1], self, self[1:] + [0])
        else:
            # this is ugly! todo: find a more pythonic way to do this!
            tuples = []
            padded = [[0] * (len(self) + 2)] + [[0] + sl + [0] for sl in self] + [[0] * (len(self) + 2)]
            for i in range(0, len(self)):
                for j in range(0, len(self)):
                    tuples.append((
                        padded[i+0][j], padded[i+0][j+1], padded[i+0][j+2],
                        padded[i+1][j], padded[i+1][j+1], padded[i+1][j+2],
                        padded[i+2][j], padded[i+2][j+1], padded[i+2][j+2],
                    ))
            return tuples

    def set_state(self, state):
        self.data = state

    def is_all_zero(self):
        return all(all(i == 0 for i in sl) for sl in self)

    def fill_ones(self):
        if self.dimension == 1:
            self.data = [1 for i in self]
        else:
            self.data = [[1 for i in sl] for sl in self]

    def set_random_state(self):
        if self.dimension == 1:
            self.data = [random.randint(0, 1) for i in self]
        else:
            self.data = [[random.randint(0, 1) for i in sl] for sl in self]


def parse_grid(grid_str, char0, char1):
    return [int(c) for c in grid_str.replace(char0, '0').replace(char1, '1')]


def delete_output_lines(n):
    print("\033[F\033[K" * n, end='\r')


def get_next_cell_state(rule, cells):
    # the rule numbers follow the Wolfram convention, so we'll need the binary
    # representation of the given number and we'll use the cells as an index
    # into that representation.
    # eg rule 54 is 00110110 (54 in binary) so, (0, 0, 0) -> 0;  (0, 0 ,1) -> 1, (0, 1, 0) -> 1, ...)
    # see http://mathworld.wolfram.com/ElementaryCellularAutomaton.html for more detail

    # the reversed() in the index and [::-1] i the rule representation are there because the least
    # significant bit is at the right, this way we conform to the Wolfram numbering scheme
    neighborhood_size = len(cells)
    rule_index = sum(i * j for i, j in zip(cells, (2**i for i in reversed(range(neighborhood_size)))))
    binary_rule_repr = bin(rule)[2:].rjust(2**neighborhood_size, '0')[::-1]
    next_states = [int(c) for c in binary_rule_repr]
    return next_states[rule_index]


def get_next_grid_state(rule, grid):
    cells = grid.get_neighbor_tuples()
    new_grid = Grid(grid.dimension, grid.size, grid.char0, grid.char1)
    new_state = [get_next_cell_state(rule, cs) for cs in cells]
    if grid.dimension == 1:
        new_grid.set_state(new_state)
    else:
        new_state = [new_state[x:x+len(grid)] for x in range(0, len(new_state), len(grid))]  # split the new_state (flat list) into chunks of the right size
        new_grid.set_state(new_state)
    return new_grid


if __name__ == '__main__':
    dimension, rule, grid_str, grid_size, steps, char0, char1 = handle_args()
    grid = Grid(dimension, grid_size, char0=char0, char1=char1)
    if dimension == 1 and grid_str is not None:
        grid.set_state(parse_grid(grid_str, char0, char1))

    if dimension == 1:
        # evolve the automaton for the given number of steps and print each one
        print(grid)
        for _ in range(steps):
            grid = get_next_grid_state(rule, grid)
            print(grid)

    if dimension == 2:
        print(grid)

        for s in range(steps):
            # sleep for a sec, refresh the grid
            time.sleep(0.3)
            grid = get_next_grid_state(rule, grid)
            delete_output_lines(len(grid))
            print(grid)
            if grid.is_all_zero():
                print('All dead after %s steps' % (s+1))
                break
