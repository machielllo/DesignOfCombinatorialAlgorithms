from instance import Instance
from solution import Solution, Index
from alns import ALNS
from construction_heuristic import construction_heuristic
# from operators import *

import argparse
parser = argparse.ArgumentParser(description='Solve a MEVRP-PL instance using ALNS.')
parser.add_argument('instance', type=str, help='Path to the instance file')
parser.add_argument('output', type=str, help='Path to the output file')
parser.add_argument('--iterations', type=int, default=1000, help='Maximum number of iterations')
parser.add_argument('--time', type=int, default=60, help='Maximum time in seconds')
parser.add_argument('--initial_temperature', type=float, default=0.1, help='Initial temperature for the ALNS algorithm')

instances = ['929.inst', '943.inst', '973.inst', '978.inst', '996.inst']

toys_path = '../Toys/Not Annotated/'

instance = Instance('../Toys/Not Annotated/996.inst')
sol = Solution(instance, name="Empty 996")
# sol._insert_empty_trip(-1)



sol.insert_cost(Index(0, 0, 1, 0), 1)
print(sol)

sol.insert_cost(Index(1, 0, 1, 0), 4)
sol.insert_cost(Index(0, 0, 1, 0), 1)


print(sol)

sol.write('test.sol', annotations=True)
sol.check_validity(verbose=True)
# solution = construction_heuristic(instance)
# print(instance.distances[0][1])

def main(args):
    instance_file = args.instance
    output_file = args.output
    instance = Instance(instance_file)
    solution = construction_heuristic(instance)
    alns = ALNS(solution)
    alns.add_destroy(random_remove_customer, 1)
    alns.add_repair(greedy_insert_customer, 1)
    solution = alns.solve(1000, 60, 0.1)
    solution.write(output_file)
    

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.instance, args.output)

from collections import Counter
routes = [[0, 1, 2, 0], [0, 6, 7, 0], [0, 2, 1, 0]]

lockers = {5: [3, 4], 6: None}

c = Counter({node: 0 for node in range(1, 5)})
for route in routes:
    c.update(route)
for locker in lockers.values():
    c.update(locker)
