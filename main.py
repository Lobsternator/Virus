__author__ = "Julius Edvardsson"
__version__ = "0.3.2a"
__copyright__ = "Copyright Virus Julius Edvardsson 2021 (©)"
__description__ = "Randomly moves windows using smooth noise."

import argparse, sys

parser = argparse.ArgumentParser(description=__description__)
parser.add_argument('--speed',            '-sp', nargs=1,   type=float, default=[0.225],
                    help='speed when moving a window (min: 0, max: inf, default: 0.225)')

parser.add_argument('--smoothing-factor', '-sm', nargs=1,   type=float, default=[0.85],
                    help='interpolation factor when moving a window (min: 0, max: 1, default: 0.85)')

parser.add_argument('--refresh-rate',     '-r',  nargs=1,   type=float, default=[60.0],
                    help='number of updates per second (min: 0, max: inf, default: 60.0)')

parser.add_argument('--blacklist',        '-b',  nargs='+', type=str,   default=[],
                    help='blacklisted executable paths')

parser.add_argument('--whitelist',        '-w',  nargs='+', type=str,   default=[],
                    help='whitelisted executable paths, overwrites blacklisted paths')

args = parser.parse_args(sys.argv[1:])

def main():
    from lib.program import Program
    
    program = Program(args)
    program.run()

if __name__ == "__main__":
    main()
