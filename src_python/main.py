from instance import Instance
from solution import Solution
from alns import ALNS
from construction_heuristic import construction_heuristic
# from operators import *
# import argparse
# parser = argparse.ArgumentParser(description='Solve a MEVRP-PL instance using ALNS.')


instance = Instance('../Toys/Not Annotated/996.inst')
solution = construction_heuristic(instance)
solution.plot()

# print(instance.distances[0][1])

def main(instance_file, output_file):
    instance = Instance(instance_file)
    solution = construction_heuristic(instance)
    alns = ALNS(solution)
    alns.add_destroy(random_remove_customer, 1)
    alns.add_repair(greedy_insert_customer, 1)
    solution = alns.solve(1000, 60, 0.1)
    solution.write(output_file)
    
