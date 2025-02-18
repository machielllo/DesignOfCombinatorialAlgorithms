import os
os.getcwd()

from instance import Instance
from solution import Solution
from vehicle import Vehicle
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
solution = construction_heuristic(instance)
print(solution.vehicles)

for vehicle in solution.vehicles.values():
    vehicle.print()

v2 = solution.vehicles[2]

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
    