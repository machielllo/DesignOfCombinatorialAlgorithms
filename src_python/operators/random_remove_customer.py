from solution import Solution
from request import Request
import numpy as np

def random_remove_customer(solution: Solution) -> Solution:
    num_to_remove = 4 # np.random.randint(1, solution.instance.num_customers)
    cid_to_remove = np.random.choice(solution.instance.customer_ids, num_to_remove, replace=False)
    new_solution = solution.copy()
    for cid in cid_to_remove:
        vid = solution.customer_assignment[cid]
        if vid is not None:
            new_solution.vehicles[vid].remove_customer(cid)
            new_solution.customer_assignment[cid] = None
            new_solution.request_list.append(Request("insert_customer", customer_id=cid))
    return new_solution
