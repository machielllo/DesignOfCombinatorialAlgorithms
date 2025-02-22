import sys
sys.path.append('/mnt/c/Users/machi/Documents/DOCA/src/')
from instance import Instance
from solution import Solution, Index
from construct import construction_heuristic

toys_path = '/mnt/c/Users/machi/Documents/DOCA/Toys/Not Annotated/'

instances = ['929.inst', '943.inst', '973.inst', '978.inst', '996.inst']

for inst in instances:
    instance = Instance(toys_path + inst)
    solution = construction_heuristic(instance)
    solution.feasible(True)
    solution.draw(file_out=inst.replace('inst', 'png'))


instance = Instance(toys_path + '973.inst')
solution = construction_heuristic(instance)

print(solution)


