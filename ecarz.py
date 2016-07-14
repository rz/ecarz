import argparse


def get_new_cell_value(rule, cells):
    # the rule numbers follow the Wolfram convention, so we'll need the binary
    # representation of the given number and we'll use the 3 cells as an index
    # into that representation.
    # eg rule 54 is 00110110 (54 in binary) so, (0, 0, 0) -> 0;  (0, 0 ,1) -> 1, (0, 1, 0) -> 1, ...)
    # see http://mathworld.wolfram.com/ElementaryCellularAutomaton.html for more detail
    binary_rule_repr = bin(rule)[2:].rjust(8, '0')
    next_states = [int(c) for c in binary_rule_repr]
    index = sum(i * j for i, j in zip(cells, (4, 2, 1)))  # this is converting a triplet of zeros and ones to base 10 eg (1, 1, 0) -> 6
    return next_states[index]


def initialize_grid():
    return [int(c) for c in '1'.center(grid_size, '0')]  # one 1 cell at the middle. hacky, but the center() method is handy


def get_new_grid(rule, grid):
    # the funny arguments in the zip are to get the boundary condition:
    # we use "blank cell" boundary conditions ie always assume there is a blank
    # cell to the left and right of the grid's ends.
    # todo: support other types of boundary conditions?
    grid_zip = zip([0] + grid[:-1], grid, grid[1:] + [0])
    new_grid = [get_new_cell_value(rule, (l, c, r)) for l, c, r in grid_zip]
    return new_grid


def grid_to_string(grid, char0, char1):
    return ''.join(str(i) for i in grid).replace('0', char0).replace('1', char1)


def parse_grid(grid_str, char0, char1):
    return [int(c) for c in grid_str.replace(char0, '0').replace(char1, '1')]


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
            '-G', '--grid', help='The initial state of the grid. Specifying this option overrides the grid-size option. By default, an empty cell is represented by a single space character and a filled cell by *, but this can be changed with the --char-zero and --char-one options.',
            type=str, default=None)
    parser.add_argument(
            '--char-zero', help='The character to use for a cell in state 0 in human-friendly representations. Default is a space.',
            type=str, default=' ')
    parser.add_argument(
            '--char-one', help='The character to use for a cell in state 1 in human-friendly representations. Default is *.',
            type=str, default='*')

    args = parser.parse_args()

    if args.grid is None:
        grid_size = args.grid_size
        grid = None
    else:
        grid_size = len(args.grid)
        grid = parse_grid(args.grid, args.char_zero, args.char_one)
    return args.rule, grid, grid_size, args.steps, args.char_zero, args.char_one


if __name__ == '__main__':
    rule, grid, grid_size, max_steps, char0, char1 = handle_args()
    if grid is None:
        grid = initialize_grid()

    print(grid_to_string(grid, char0, char1))  # initial step

    # evolve the automaton for the given number of steps and print each one
    for _ in range(max_steps):
        grid = get_new_grid(rule, grid)
        print(grid_to_string(grid, char0, char1))

