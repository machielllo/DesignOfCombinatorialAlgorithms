from instance import *
from solution import *
import time
import numpy as np

class ALNS:
    def __init__(self, instance, solution):
        self.instance = instance
        self.repair_weights = []
        self.destroy_weights = []
        self.repair_operators = []
        self.destroy_operators = []
        self.best_solution = solution
        self.current_solution = solution
        
    def add_repair(self, repair, weight):
        self.repair_operators.append(repair)
        self.repair_weights.append(weight)
    
    def add_destroy(self, destroy, weight):
        self.destroy_operators.append(destroy)
        self.destroy_weights.append(weight)
    
    def roullette_wheel(self):
        pass
    
    def update_weights(self, destroy_idx, repair_idx):
        pass
        
    def solve(self, max_iter, max_time, temperature) -> Solution:
        it = 0
        start_time = time.time()
        current_time = time.time()
        while it <= max_iter and current_time - start_time <= max_time:
            destroy_idx, repair_idx = self.roullette_wheel()
            new_solution = self.repair_operators[repair_idx](
                self.destroy_operators[destroy_idx](self.current_solution)
            )
            if new_solution.cost <= self.best_solution.cost:
                self.best_solution = new_solution
            if new_solution.cost <= self.current_solution.cost:
                self.current_solution = new_solution
            else:
                delta = new_solution.cost - self.current_solution.cost
                if np.random.rand() < np.exp(-delta / temperature):
                    self.current_solution = new_solution
            self.update_weights(destroy_idx, repair_idx)
            it += 1
            current_time = time.time()