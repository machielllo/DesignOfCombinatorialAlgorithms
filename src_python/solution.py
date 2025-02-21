from instance import Instance
from request import Request
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import Counter
from collections import namedtuple
from copy import deepcopy

ID = int

class Index:
    def __init__(self, route: int, trip: int = 0, index: int = 1, locker: ID = 0):
        self.route = route
        self.trip = trip
        self.index = index
        self.locker = locker

    def copy(self):
        return Index(self.route, self.trip, self.index, self.locker)
    
    def __repr__(self):
        return f"Index(route={self.route}, trip={self.trip}, index={self.index}, locker={self.locker})"

class Solution:
    def __init__(
            self,
            instance: Instance,
            routes: list[list[list[ID]]] = None,
            loads: list[list[int]] = None,
            time: list[list[list[float]]] = None,
            charge: list[list[list[float]]] = None,
            indices: dict[ID, Index] = None,
            lockers: dict[ID, list[ID]] = None,
            name: str = "",
            requests: list[Request] = [],
    ):
        self.instance = instance

        if routes is None:
            self.routes = [[[0, 0]] for _ in range(instance.num_vehicles)]
        else:
            self.routes = routes

        if loads is None:
            self.loads = [[0] for _ in range(instance.num_vehicles)]
        else:
            self.loads = loads

        if time is None:
            self.time = [[[0.0, 0.0]] for _ in range(instance.num_vehicles)]
        else:
            self.time = time

        if charge is None:
            self.charge = [[[-instance.initial_charge[i], -instance.initial_charge[i]]]
                           for i in range(instance.num_vehicles)]
        else:
            self.charge = charge

        if lockers is None:
            self.lockers = {ID: [] for ID in instance.locker_ids}
            
        if indices is None:
            self.indices = {cid: None for cid in instance.customer_ids}
        else:
            self.indices = indices

        self.name = name
        self.requests = requests

    def total_cost(self) -> float:
        "Calculate the total cost of the solution"
        total = 0.0
        total += self._distance_cost()
        total += self._deployment_cost()
        total += self._locker_cost()
        total += self._penalty_customer_cost()
        total += self._penalty_depot_cost()
        return total
        
    def insert(self, index: Index, node: ID):
        if index.trip >= len(self.routes[index.route]):
            self._insert_empty_trip()
            index.trip = len(self.routes[index.route])
            index.index = 1

        if node in self.instance.customer_ids:
            self._insert_customer(index, node)

        if node in self.instance.locker_ids:
            self._insert_locker(index, node)

        if node in self.instance.charger_ids:
            self._insert_charger(index, node)

    def _insert_locker(self, index: Index, node: ID):
        prev_index = index.copy()
        prev_index.index -= 1
        removed_arc = (self._node_at(prev_index), self._node_at(index))
        added_arc1 = (self._node_at(prev_index), node)
        added_arc2 = (node, self._node_at(index))
        
        d_charge = self._charge_cost(*added_arc1) + self._charge_cost(*added_arc2) -\
            self._charge_cost(*removed_arc)

        d_travel_time = self._travel_time(*added_arc1) + self._travel_time(*added_arc2) -\
            self._travel_time(*removed_arc)

        prev_charge_index = self._previous_charge_index(index)
        prev_charge = self._charge_at(prev_charge_index)
        next_charge_index = self._next_charge_index(index)
        next_charge = self._charge_at(next_charge_index)
        
        if prev_charge + d_charge <= 0:
            d_charge_time = 0
            d_charge_next = d_charge
        elif prev_charge < 0:
            d_charge_time = (prev_charge + d_charge) / self.instance.rate_recharge
            d_charge_next = -prev_charge
        else:
            d_charge_time = d_charge / self.instance.rate_recharge
            d_charge_next = 0

        d_time_to_next_charge = d_charge_time + \
            self.instance.service_time[node] + d_travel_time
        d_time_after_next_charge = d_time_to_next_charge +\
            max(0, d_charge_next + next_charge) / self.instance.rate_recharge
        
        new_time = self.time[index.route][index.trip][index.index - 1] + self.instance.service_time[node] +\
            d_charge_time + self._travel_time(*added_arc1)

        ## Update time
        idx = prev_charge_index.copy()
        idx.index += 1
        start = idx.index
        for pnode in self.routes[index.route][index.trip][start:index.index]:
            self.time[idx.route][idx.trip][idx.index] += d_charge_time
        
        for pnode in self.routes[index.route][index.trip][index.index:next_charge_index.index]:
            self.time[idx.route][idx.trip][idx.index] += d_time_to_next_charge

        for pnode in self.routes[index.route][index.trip][next_charge_index.index:]:
            self.time[idx.route][idx.trip][idx.index] += d_time_after_next_charge

        for trip in self.routes[index.route][(index.trip+1):]:
            idx.trip += 1
            idx.index = 0
            for _ in range(len(trip)):
                self.time[idx.route][idx.trip][idx.index] += d_time_after_next_charge

        self.loads[index.route][index.trip] += self.instance.demand[node]
        self.routes[index.route][index.trip].insert(index.index, node)
        self.charge[index.route][index.trip].insert(index.index, 0)
        self.time[index.route][index.trip].insert(index.index, new_time)
        self.indices[node] = index

        

    def _insert_customer(self, index: Index, node: ID):
        prev_index = index.copy()
        prev_index.index -= 1
        removed_arc = (self._node_at(prev_index), self._node_at(index))
        added_arc1 = (self._node_at(prev_index), node)
        added_arc2 = (node, self._node_at(index))

        d_charge = self._charge_cost(*added_arc1) + self._charge_cost(*added_arc2) -\
            self._charge_cost(*removed_arc)

        d_travel_time = self._travel_time(*added_arc1) + self._travel_time(*added_arc2) -\
            self._travel_time(*removed_arc)
        
        prev_charge_index = self._previous_charge_index(index)
        prev_charge = self._charge_at(prev_charge_index)
        next_charge_index = self._next_charge_index(index)
        next_charge = self._charge_at(next_charge_index)
        
        if prev_charge + d_charge <= 0:
            d_charge_time = 0
            d_charge_next = d_charge
        elif prev_charge < 0:
            d_charge_time = (prev_charge + d_charge) / self.instance.rate_recharge
            d_charge_next = -prev_charge
        else:
            d_charge_time = d_charge / self.instance.rate_recharge
            d_charge_next = 0

        d_time_to_next_charge = d_charge_time + \
            self.instance.service_time[node] + d_travel_time
        d_time_after_next_charge = d_time_to_next_charge +\
            max(0, d_charge_next + next_charge) / self.instance.rate_recharge
        
        new_time = self.time[index.route][index.trip][index.index - 1] + self.instance.service_time[node] +\
            d_charge_time + self._travel_time(*added_arc1)

        ## Update charge        
        self.charge[prev_charge_index.route][prev_charge_index.trip][prev_charge_index.index] += d_charge
        self.charge[next_charge_index.route][next_charge_index.trip][next_charge_index.index] += d_charge_next
        
        ## Update time
        idx = prev_charge_index.copy()
        idx.index += 1
        start = idx.index
        for pnode in self.routes[index.route][index.trip][start:index.index]:
            self.time[idx.route][idx.trip][idx.index] += d_charge_time
        
        for pnode in self.routes[index.route][index.trip][index.index:next_charge_index.index]:
            self.time[idx.route][idx.trip][idx.index] += d_time_to_next_charge
            if pnode in self.indices:
                self.indices[pnode].index += 1

        for pnode in self.routes[index.route][index.trip][next_charge_index.index:]:
            self.time[idx.route][idx.trip][idx.index] += d_time_after_next_charge
            if pnode in self.indices:
                self.indices[pnode].index += 1

        for trip in self.routes[index.route][(index.trip+1):]:
            idx.trip += 1
            idx.index = 0
            for _ in range(len(trip)):
                self.time[idx.route][idx.trip][idx.index] += d_time_after_next_charge
                if pnode in self.indices:
                    self.indices[pnode].index += 1

        self.loads[index.route][index.trip] += self.instance.demand[node]
        self.routes[index.route][index.trip].insert(index.index, node)
        self.charge[index.route][index.trip].insert(index.index, 0)
        self.time[index.route][index.trip].insert(index.index, new_time)
        self.indices[node] = index
        
    def remove_at(self, index: Index):
        if node in self.instance.customer_ids:
            self.indices[node] = None
        self.routes[index.route][index.trip].pop(index.index)
        # Update costs etc
        # Add requests

    def remove_customer(self, node: ID):
        index = self.indices[node]
        self.remove_at(index)

    def insert_cost(self, index: Index, node: ID):
        if node in self.instance.customer_ids:
            return self._insert_cost_customer(index, node)
        if node in self.instance.charger_ids:
            return self._insert_cost_charger(index, node)
        if node in self.instance.locker_ids:
            return self._insert_cost_locker(index, node)
        if node == 0:
            return self._insert_cost_depot(index, node)

    def _insert_cost_customer(self, index: Index, node: ID) -> float:
        if index.index == 0:
            raise ValueError("Can't insert before first depot")
        if index.index == len(self.routes[index.route][index.trip]):
            raise ValueError("Can't insert after last depot")
        
        added_load = self.instance.demand[node]
        if self.loads[index.route][index.trip] + added_load > self.instance.capacity_volume:
            return np.inf
        removed_arc = (self.routes[index.route][index.trip][index.index - 1],
                       self.routes[index.route][index.trip][index.index])
        added_arc1 = (self.routes[index.route][index.trip][index.index - 1], node)
        added_arc2 = (node, self.routes[index.route][index.trip][index.index])
        d_distance = self._distance(*added_arc1) + self._distance(*added_arc2) - self._distance(*removed_arc)
        d_charge = d_distance * self.instance.rate_discharge
        prev_charge_index = self._previous_charge_index(index)
        prev_charge = self.charge[index.route][index.trip][prev_charge_index.index]
        next_charge_index = self._next_charge_index(index)
        next_charge = self.charge[index.route][index.trip][next_charge_index.index]
        
        if prev_charge + d_charge > self.instance.capacity_battery:
            return np.inf
        
        if prev_charge + d_charge <= 0:
            d_charge_time = 0
            d_charge_next = d_charge
        elif prev_charge < 0:
            d_charge_time = (prev_charge + d_charge) / self.instance.rate_recharge
            d_charge_next = -prev_charge
        else:
            d_charge_time = d_charge / self.instance.rate_recharge
            d_charge_next = 0

        d_time_to_next_charge = d_charge_time + \
            self.instance.service_time[node] + d_distance / self.instance.speed
        d_time_after_next_charge = d_time_to_next_charge +\
            max(0, d_charge_next + next_charge) / self.instance.rate_recharge
        
        new_time = self.time[index.route][index.trip][index.index - 1] + self.instance.service_time[node] +\
            d_charge_time + self._travel_time(*added_arc1)

        # Additional travel cost
        cost = d_distance * self.instance.cost_distance
        
        # Additional deployment cost
        if self.routes[index.route] == [[0, 0]]:
            cost += self.instance.cost_deployment

        ## Additional deadline penalties
        idx = prev_charge_index.copy()
        idx.index += 1
        start = idx.index
        for pnode in self.routes[index.route][index.trip][start:index.index]:
            cost += self._additional_penalty(idx, d_charge_time)
            idx.index += 1
        
        for pnode in self.routes[index.route][index.trip][index.index:next_charge_index.index]:
            cost += self._additional_penalty(idx, d_time_to_next_charge)
            idx.index += 1
                
        for pnode in self.routes[index.route][index.trip][next_charge_index.index:]:
            cost += self._additional_penalty_customer(idx, d_time_after_next_charge)
            idx.index += 1

        for trip in self.routes[index.route][(index.trip+1):]:
            idx.trip += 1
            idx.index = 0
            for _ in range(len(trip)):
                cost += self._additional_penalty(idx, d_time_after_next_charge)
                idx.index += 1

        return cost

    def _additional_penalty(self, index: Index, d_time: float) -> float:
        node = self._node_at(index)
        if node in self.instance.customer_ids:
            return self._additional_penalty_customer(index, d_time)
        if node in self.instance.locker_ids:
            return self._additional_penalty_customer(index, d_time)
        if node == 0 and \
           index.trip == len(self.route[index.route]) and \
           index.index == len(self.route[index.route][index.trip]):
            return self._additional_penalty_depot(index, d_time)
            
    def _additional_penalty_locker(self, index: Index, d_time: float) -> float:
        node = self._node_at(index)
        time = self._time_at(index)
        cost = 0.0
        for customer in self.lockers[node]:
            deadline = self.instance.deadline[customer]
            if time + d_time <= deadline:
                cost +=  0.0
            elif time < deadline:
                cost += (time + d_time - deadline) * self.instance.cost_penalty_customer
            else:
                cost += d_time * self.instance.cost_penalty_customer
        return cost
        
    def _additional_penalty_customer(self, index: Index, d_time: float) -> float:
        node = self._node_at(index)
        time = self._time_at(index)
        deadline = self.instance.deadline[node]
        if time + d_time <= deadline:
            return 0.0
        elif time < deadline:
            return (time + d_time - deadline) * self.instance.cost_penalty_customer
        else:
            return d_time * self.instance.cost_penalty_customer

    def _additional_penalty_depot(self, index: Index, d_time: float) -> float:
        time = self.time[index.route][-1][-1]
        deadline = self.instance.deadline[0]
        if time + d_time <= deadline:
            return 0.0
        elif time < deadline:
            return (time + d_time - deadline) * self.instance.cost_penalty_depot
        else:
            return d_time * self.instance.cost_penalty_depot

    def _previous_charge_index(self, index: Index) -> Index:
        idx = index.copy()
        idx.index -= 1
        while self._node_at(idx) not in self.instance.chargable_ids:
            idx.index -= 1
        return idx

    def _next_charge_index(self, index: Index) -> Index:
        idx = index.copy()
        while self._node_at(idx) not in self.instance.chargable_ids:
            idx.index += 1
        return idx
        
    def _node_at(self, index: Index) -> ID:
        return self.routes[index.route][index.trip][index.index]

    def _time_at(self, index: Index) -> float:
        return self.time[index.route][index.trip][index.index]

    def _load_at(self, index: Index) -> int:
        return self.load[index.route][index.trip]

    
    def _charge_at(self, index: Index) -> float:
        return self.charge[index.route][index.trip][index.index]
        
    def remove_cost(self, index: Index) -> float:
        pass

    def removal_cost_customer(self, node: ID) -> float:
        index = self.indices[node]
        if index is None:
            return 0.0
        return self.removal_cost(index)

        
    def check_validity(self, verbose: bool = False) -> bool:
        valid = True
        if not self._check_charge(verbose):
            valid = False
        if not self._check_volume(verbose):
            valid = False
        if not self._check_count(verbose):
            valid = False
        if not self._check_cycle(verbose):
            valid = False
        return valid

    ### Private Methods

    # easy acces
    def _distance(self, node1: ID, node2:  ID) -> float:
        return float(self.instance.distance.loc[node1, node2])

    def _travel_time(self, node1: ID, node2: ID) -> float:
        return float(self.instance.travel_time.loc[node1, node2])

    def _charge_cost(self, node1: ID, node2: ID) -> float:
        return float(self.instance.charge_cost.loc[node1, node2])

    def _locker_volume(self, node: ID) -> int:
        "Return the demand associated with locker node"
        demand = 0
        for node in self.locker[node]:
            demand += self.instance.demand[node]
        return demand

    def _distance_cost(self) -> float:
        return self._total_distance() * self.instance.cost_distance

    def _total_distance(self) -> float:
        total = 0
        for route in self.routes:
            for trip in route:
                prev = 0
                for node in trip[1:]:
                    total += self._distance(prev, node)
                    prev = node
        return total
        
    def _deployment_cost(self) -> float:
        total = 0
        for route in self.routes:
            if route[0] != [0, 0]:
                total += self.instance.cost_deployment
        return total
    
    def _locker_cost(self) -> float:
        total = 0
        for assigned in self.lockers.values():
            if assigned:
                total += self.instance.cost_locker
        return total
    
    def _penalty_customer_cost(self) -> float:
        total = 0
        for i, route in enumerate(self.routes):
            for j, trip in enumerate(route):
                for k, node in enumerate(trip):
                    if node in self.instance.customer_ids:
                        total += max(0, self.time[i][j][k] - self.instance.deadline[node])
                    if node in self.instance.locker_ids:
                        total += sum(max(0, self.time[i][j][k] - self.instance.deadline[n])
                                     for n in self.lockers[node])
        return total * self.instance.cost_penalty_customer
    
    def _penalty_depot_cost(self) -> float:
        total = 0
        for dt in self.time:
            total += max(0, dt[-1][-1] - self.instance.deadline[0])
        return total * self.instance.cost_penalty_depot
    
    def _check_volume(self, verbose: bool) -> bool:
        "Check if capacity is violated"
        valid = True
        for i, route in enumerate(self.routes):
            for j, trip in enumerate(route):
                total_demand = 0
                for node in trip:
                    if node in self.instance.customer_ids:
                        total_demand += self.instance.demand[node]
                    elif node in self.instance.locker_ids:
                        total_demand += self._locker_volume(node)
                if total_demand > self.instance.capacity_volume:
                    verbose and print(f"Vehicle {i + 1} is overloaded on trip {j}")
                    valid = False
        return valid

    def _check_charge(self, verbose: bool) -> bool:
        "Check if charge constraints are violated"
        valid = True
        for i, route in enumerate(self.routes):
            charge = self.instance.initial_charge[i] + max(0, self.charge[i][0][0])
            prev = 0
            for j, trip in enumerate(route):
                for k, node in enumerate(trip):
                    charge -= self._charge_cost(prev, node)
                    prev = node
                    charge += max(0, self.charge[i][j][k])
                    if node not in self.instance.chargable_ids and self.charge[i][j][k] != 0:
                        verbose and print(f"Vehicle {i + 1} gets charged at {node}")                    
                    if charge > self.instance.capacity_battery:
                        verbose and print(f"Vehicle {i + 1} is overcharged at {node}")
                        valid = False
                    if charge < 0:
                        verbose and print(f"Vehicle {i + 1} is undercharged at {node}")
                        valid = False
        return valid
            
    def _check_cycle(self, verbose: bool) -> bool:
        "Check if we start and end at depot"
        valid = True
        for i, route in enumerate(self.routes):
            for j, trip in enumerate(route):
                if trip[0] != 0:
                    verbose and print(f"Vehicle {i + 1} does not start at depot on trip {j}")
                    valid = False
                if trip[-1] != 0:
                    verbose and print(f"Vehicle {i + 1} does not end at depot on trip {j}")
                    valid = False
        return valid

    def _check_count(self, verbose: bool) -> bool:
        "Check if customers and lockers are assigned once and if lockers are assigned when used"
        valid = True
        c = Counter()
        for route in self.routes:
            for trip in route:
                c.update(trip)
            
        for node, locker in self.lockers.items():
            if locker and node not in c:
                verbose and print(f"Locker {node} used but not assigned")
                valid = False
                c.update(locker)
            if c[node] > 1:
                verbose and print(f"Locker {node} visited multiple times")
                
        for node in self.instance.customer_ids:
            if node not in c:
                verbose and print(f"Customer {node} not assigned")
                valid = False
            if c[node] > 1:
                verbose and print(f"Customer {node} assigned multiple times")
                valid = False
        return valid

    def _insert_empty_trip(self, i: int):
        "Insert an empty trip for vehicle i - 1"
        self.routes[i].append([0, 0])
        self.loads[i].append(0)
        self.charge[i].append([self.charge[i][-1][-1], self.charge[i][-1][-1]])
        self.time[i].append([self.time[i][-1][-1], self.time[i][-1][-1]])

    
    # maybe
    def copy(self):
        return Solution(
            instance = self.instance,
            routes=deepcopy(self.routes),
            time=deepcopy(self.time),
            charge=deepcopy(self.charge),
            indices=deepcopy(self.indices),
            lockers=deepcopy(self.lockers),
            name=self.name,
            # cost=self.cost,
            requests=deepcopy(self.requests)
        )

    
    ### Write and draw
    def write(self, file_path: str, annotations: bool = False):
        with open(file_path, 'w') as f:
            f.write(str(self.instance.instance_id))
            if annotations:
                f.write(" // ID of the instance this solution solves")
            f.write("\n")

            f.write(self.name)
            if annotations:
                f.write(" // Name for your solution (e.g. seed, #iterations, random json str, etc)")
            f.write("\n")

            f.write(str(int(self.check_validity())))
            if annotations:
                f.write(" // 1 iff we believe this solution is feasible, otherwise 0")
            f.write("\n")

            f.write(f"{self.total_cost():.3f}")
            if annotations:
                f.write(" // Total objective (real)")
            f.write("\n")

            f.write(f"{self._locker_cost():.3f}")
            if annotations:
                f.write(" // Locker open cost (real)")
            f.write("\n")

            f.write(f"{self._deployment_cost():.3f}")
            if annotations:
                f.write(" // Vehicle deploy cost (real)")
            f.write("\n")

            f.write(f"{self._distance_cost():.3f}")
            if annotations:
                f.write(" // Distance cost (real)")
            f.write("\n")

            f.write(f"{self._penalty_customer_cost():.3f}")
            if annotations:
                f.write(" // Lateness penalty at customers (real)")
            f.write("\n")

            f.write(f"{self._penalty_depot_cost():.3f}")
            if annotations:
                f.write(" // Lateness penalty at depot (real)")
            f.write("\n")

            lockers = []
            for i in range(1, self.instance.num_customers + 1):
                index = self.indices[i]
                if index is None:
                    lockers.append(str(0))
                else:
                    lockers.append(str(index.locker))
            f.write(", ".join(lockers))
            if annotations:
                f.write(
                    " // Indicator of locker delivery for every customer 1, ..., n (0 if home delivery; locker's node ID, if locker delivery; empty line if n = 0)")
            f.write("\n")

            for i in range(len(self.routes)):
                vid = i + 1
                trips = len(self.routes[i])
                route_line = f"{vid}, " + ", ".join(
                    str(node) for j in range(trips) for node in self.routes[i][j]
                )
                f.write(route_line)
                if annotations:
                    f.write(f" // Route vehicle {vid}")
                f.write("\n")

                cq_line = f"{vid}, " + ", ".join(
                    f"{max(0, q):.3f}" for j in range(trips) for q in self.charge[i][j]
                )
                f.write(cq_line)
                if annotations:
                    f.write(f" // Charge quantities vehicle {vid}")
                f.write("\n")

                ut_line = f"{vid}, " + ", ".join(
                    f"{ut:.4f}" for j in range(trips) for ut in self.time[i][j]
                )
                f.write(ut_line)
                if annotations:
                    f.write(f" // Unloading completion time vehicle {vid}")
                f.write("\n")
                
    def draw(self, ax=None):
        "Plot the solution"
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 12))
            show = True
        else:
            show = False
        
        depot = self.instance.location[0]
        ax.scatter(depot[0], depot[1], marker='s', color='blue')
        customers_x = [self.instance.location[cid][0] for cid in self.instance.customer_ids]
        customers_y = [self.instance.location[cid][1] for cid in self.instance.customer_ids]
        ax.scatter(customers_x, customers_y, marker='x', color='blue')
        chargers_x = [self.instance.location[cid][0] for cid in self.instance.charger_ids]
        chargers_y = [self.instance.location[cid][1] for cid in self.instance.charger_ids]
        ax.scatter(chargers_x, chargers_y, marker='P', color='yellow')
        lockers_x = [self.instance.location[cid][0] for cid in self.instance.locker_ids]
        lockers_y = [self.instance.location[cid][1] for cid in self.instance.locker_ids]
        ax.scatter(lockers_x, lockers_y, marker='^', color='red')
        for x, y in zip(lockers_x, lockers_y):
            circle = patches.Circle((x, y), self.instance.locker_radius, edgecolor='red',
                                    facecolor='none', linewidth=2)
            ax.add_patch(circle)
        max_distance = self.instance.capacity_battery / self.instance.rate_discharge
        for x, y in zip(chargers_x, lockers_y):
            circle = patches.Circle((x, y), max_distance, edgecolor='none',
                                    facecolor='paleturquoise', linewidth=2, alpha=0.5)
            ax.add_patch(circle)
        circle = patches.Circle((depot[0], depot[1]), max_distance,
                                edgecolor='none', facecolor='paleturquoise', linewidth=2, alpha=0.2)
        ax.add_patch(circle)

        for route in self.routes:
            for trip in route:
                location = [self.instance.location[ID] for ID in trip]
                x, y = zip(*location)
                ax.plot(x, y)
        
        ax.grid(False)
        ax.relim()
        ax.autoscale()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.axis('off') 

        ax.set_aspect('equal')
        if show:
            fig.show()

    def __repr__(self):
        full = self.name + f"\ncost: {self.total_cost()}\n"
        full += f"feasible: {self.check_validity()}\n"
        full += f"routes:\t {self.routes}\n"
        full += f"loads:\t {self.loads}\n"
        full += f"charge:\t {self.charge}\n"
        full += f"time:\t {self.time} \n"
        full += f"lockers: {self.lockers}"
        return full
