from solution import Solution
from request import Request
import numpy as np

def random_remove_customer(solution: Solution) -> Solution:
    num_to_remove = np.random.randint(
        int(0.2 * solution.instance.num_customers + 0.5),
        int(0.8 * solution.instance.num_customers - 0.5)
    )
    cid_to_remove = np.random.choice(solution.instance.customer_ids, num_to_remove, replace=False)
    new_solution = solution.copy()
    for cid in cid_to_remove:
        vid, trip, locker_id = new_solution.customer_assignment[cid]
        if locker_id != 0:
            # for now only remove them if they are not assigned to a locker
            continue
        new_solution.vehicles[vid].remove(cid, trip)
        new_solution.customer_assignment[cid] = None
        new_solution.request_list.append(Request("insert_customer", customer_id=cid))
    return new_solution
