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
    
    def roulette_wheel(self):
        # Select a destroy operator index using roulette-wheel selection
        # using the same method as in Ropke and Pissinger in their 2010 paper.
        total_destroy = sum(self.destroy_weights)
        r = np.random.rand() * total_destroy
        cumulative = 0
        for idx, weight in enumerate(self.destroy_weights):
            cumulative += weight
            if r <= cumulative:
                destroy_idx = idx
                break

        # Select a repair operator index
        total_repair = sum(self.repair_weights)
        r = np.random.rand() * total_repair
        cumulative = 0
        for idx, weight in enumerate(self.repair_weights):
            cumulative += weight
            if r <= cumulative:
                repair_idx = idx
                break

        return destroy_idx, repair_idx

    def update_weights(self, destroy_idx, repair_idx, score):
        """
        Update weights as explained in Ropke en Pissinger.
        """
        decay = 0.1
        self.destroy_weights[destroy_idx] = ((1 - decay) *
                                             self.destroy_weights[destroy_idx] +
                                             decay * score)
        self.repair_weights[repair_idx] = ((1 - decay) *
                                           self.repair_weights[repair_idx] +
                                           decay * score)

    def solve(self, max_iter, max_time, temperature) -> Solution:
        it = 0
        start_time = time.time()
        while it <= max_iter and time.time() - start_time <= max_time:
            # Select operators using roulette-wheel selection
            destroy_idx, repair_idx = self.roulette_wheel()

            new_solution = self.repair_operators[repair_idx](
                self.destroy_operators[destroy_idx](self.current_solution)
            )

            # Score scheme (as in Ropke and Pissinger, 2010):
            #   w_1 - 10 if the new solution is a new global best
            #   w_2 - 5 if the new solution is better than the current one
            #   w_3 - 2 if the new solution is accepted by SA accepteance criterion
            #   w_4 - 0 if the new solution is rejected
            if new_solution.cost < self.best_solution.cost:
                score = 10
            elif new_solution.cost < self.current_solution.cost:
                score = 5
            else:
                delta = new_solution.cost - self.current_solution.cost
                if np.random.rand() < np.exp(-delta / temperature):
                    score = 2
                else:
                    score = 0

            # Acceptance criteria:
            if score > 0:
                self.current_solution = new_solution
            if new_solution.cost < self.best_solution.cost:
                self.best_solution = new_solution

            # Update the weights for the operators used
            self.update_weights(destroy_idx, repair_idx, score)

            it += 1


        return self.best_solution
        
    # def solve(self, max_iter, max_time, temperature) -> Solution:
    #     it = 0
    #     start_time = time.time()
    #     current_time = time.time()
    #     while it <= max_iter and current_time - start_time <= max_time:
    #         destroy_idx, repair_idx = self.roullette_wheel()
    #         new_solution = self.repair_operators[repair_idx](
    #             self.destroy_operators[destroy_idx](self.current_solution)
    #         )
    #         if new_solution.cost <= self.best_solution.cost:
    #             self.best_solution = new_solution
    #         if new_solution.cost <= self.current_solution.cost:
    #             self.current_solution = new_solution
    #         else:
    #             delta = new_solution.cost - self.current_solution.cost
    #             if np.random.rand() < np.exp(-delta / temperature):
    #                 self.current_solution = new_solution
    #         self.update_weights(destroy_idx, repair_idx)
    #         it += 1
    #         current_time = time.time()