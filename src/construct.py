from instance import Instance
from solution import Solution, Index
# from collections import deque
import heapq
import copy
from itertools import cycle


def construction_heuristic(instance: Instance) -> Solution:
    "Construct an initial feasible solution"
    unassigned = copy.copy(instance.customer_ids)
    solution = Solution(instance, name="Initial Solution")
    tree = make_tree(instance)
    # first select the vehicle with the largest initial_charge
    vehicles = list(range(instance.num_vehicles))
    vehicles.sort(key=lambda x: instance.initial_charge[x], reverse=True)
    vehicles = cycle(vehicles)

    while unassigned:
        route = next(vehicles)
        trip = solution.next_empty_trip(route)
        customer = unassigned.pop()
        path = shortest_path(tree, 0, customer, instance)
        if path[-2] in instance.locker_ids:
            locker = path[-2]
            # add it back, as we may not assign it
            unassigned.add(customer)
            customers = set(tree[locker]).intersection(unassigned)
            # Cannot visit locker again.  Remove here so we can find
            # the customers that can only be served through the locker
            del tree[locker]
            must_assign = []
            for customer in customers:
                if shortest_path(tree, 0, customer, instance) is None:
                    must_assign.append(customer)
            for customer in must_assign:
                solution.add_to_locker(locker, customer)
                unassigned.remove(customer)
                customers.remove(customer)
            if solution._demand(locker) > instance.capacity_volume:
                raise ValueError(f"Instance invalid? Locker {locker} too full")
            # Try adding more customers to locker
            for customer in customers:
                if (
                    solution._demand(locker) + solution._demand(customer)
                    <= instance.capacity_volume
                ):
                    solution.add_to_locker(locker, customer)
                    unassigned.remove(customer)
                if solution._demand(locker) == instance.capacity_volume:
                    break
            # If no customers were added to the locker, break
            if not solution.lockers[locker]:
                break
            # insert up to (and including) locker in trip
            for node in path[1:-1]:
                solution.insert(Index(route, trip, -1, 0), node)
            charge_remaining = (
                instance.capacity_battery
                - instance.charge_required.loc[path[-3], path[-2]]
            )
            path = path[:-1]
        else:
            # insert path into trip
            for node in path[1:]:
                solution.insert(Index(route, trip, -1, 0), node)
            charge_remaining = (
                instance.capacity_battery
                - instance.charge_required.loc[path[-2], path[-1]]
            )
        node = path.pop()
        while path:
            prev = path[-1]
            if not unassigned:
                break
            if solution.loads[route][trip] >= instance.capacity_volume:
                break

            nn = min(unassigned, key=lambda x: instance.distance.loc[node, x] +
                     instance.distance.loc[x, prev])

            load_ok = (
                solution.loads[route][trip] + instance.demand[nn]
            ) <= instance.capacity_volume
            charge_ok = (
                instance.charge_required.loc[node, nn]
                + instance.charge_required.loc[nn, prev]
            ) < charge_remaining

            if load_ok and charge_ok:
                solution.insert(Index(route, trip, -1, 0), nn)
                unassigned.remove(nn)
                node = nn
                charge_remaining -= instance.charge_required.loc[node, nn]
                break
            elif prev != 0:
                solution.insert(Index(route, trip, -1, 0), prev)
            node = path.pop()
            charge_remaining = instance.capacity_battery

        for node in path[-1:0:-1]:
            solution.insert(Index(route, trip, -1, 0), node)
            
    return solution

def make_tree(instance: Instance) -> dict:
    "Do we need this tree here?"
    tree = {
        0: [
            customer
            for customer in instance.customer_ids
            if 2 * instance.distance.loc[0, customer] <= instance.radius_chargable
        ]
        + [
            locker
            for locker in instance.locker_ids
            if 2 * instance.distance.loc[0, locker] <= instance.radius_chargable
        ]
        + [
            charger
            for charger in instance.charger_ids
            if instance.distance.loc[0, charger] <= instance.radius_chargable
        ]
    }
    for charger in instance.charger_ids:
        tree[charger] = (
            [
                customer
                for customer in instance.customer_ids
                if 2 * instance.distance.loc[charger, customer]
                <= instance.radius_chargable
            ]
            + [
                locker
                for locker in instance.locker_ids
                if 2 * instance.distance.loc[charger, locker]
                <= instance.radius_chargable
            ]
            + [
                charger2
                for charger2 in instance.charger_ids
                if charger != charger2
                and instance.distance.loc[charger, charger2]
                <= instance.radius_chargable
            ]
        )
    for locker in instance.locker_ids:
        tree[locker] = [
            customer
            for customer in instance.customer_ids
            if instance.distance.loc[locker, customer] <= instance.radius_locker
        ]
    return tree

def shortest_path(tree, start, goal, instance):
    "Find the shortest path, kind of"
    pq = [(0, start, [])]  # (cost, current_node, path)
    visited = set()
    while pq:
        cost, node, path = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]
        if node == goal:
            return path
        for neighbor in tree.get(node, []):
            if neighbor not in visited:
                edge_cost = 0.0 if node in instance.locker_ids else instance.distance.loc[node, neighbor]
                heapq.heappush(pq, (cost + edge_cost, neighbor, path))
    return None 
