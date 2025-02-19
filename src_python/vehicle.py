from instance import Instance
from copy import deepcopy
import numpy as np

class Vehicle:
    def __init__(
        self,
        instance: Instance,
        ID: int,
        route: list = [0, 0],
        load: list = [0],
        recharge_quantity: list = [0, 0],
        cost: float = 0,
        departure_times = [0, 0]
    ):
        self.instance = instance
        self.ID = ID
        self.route = route
        self.load = load
        self.recharge_quantity = recharge_quantity
        self.cost = cost
        self.departure_times = departure_times
        
    def copy(self):
        return Vehicle(
            instance=self.instance,
            ID=self.ID,
            route=self.route.copy(),
            load=self.load.copy(),
            recharge=self.recharge_quantity.copy(),
            departure_time = self.departure_times.copy(),
            cost=self.cost,
        )

    def _distance(node1, node2):
        return self.instance.distances.loc[node1, node2].value

    def _prev_charger_idx(self, idx) -> int:
        while idx:
            idx -= 1
            if self.route[idx] in self.instance.charge_spots:
                break
        return idx

    def insert_cost_customer(self, idx: int, node: int) -> float:
        "calculate cost of insertion, does not include lockers"
        # First we check if the vehicle load can handle it
        if load[idx] + self.instance.demands[node] > self.instance.volume_capacity:
            return np.inf
        
        added_distance = self.distance(self.route[idx-1], node) +\
            self.distance(node, self.route[idx]) -\
            self.distance(self.route[idx-1], self.route[idx])

        added_charge = added_distance * self.instance.discharge_rate
        if added_charge > self.instance.battery_capacity:
            return np.inf

        prev_charger = self._prev_charger_idx(idx)
        prev_recharge_quantity = self.recharge_quantity[prev_charger]
        
        if added_charge + prev_recharge_quantity > self.instance.battery_capacity:
            return np.inf

        if added_charge + prev_recharge_quantity < 0:
            added_charge_time = 0
        else:
            added_charge_time = (added_charge + min(prev_recharge_quantity, 0)) / self.instance.discharge_rate

        departure_time = self.departure_times[idx-1] +\
            self.distance(self.route[idx-1], node) / self.instance.speed + \
            added_charge_time + self.instance.service_times[node]

        delay = departure_time + self.distance(node, self.route[idx]) / self.instance.speed +\
            self.instance.service_times[self.route[idx]] - self.departure_times[idx]
        
        cost = added_distance * self.instance.travel_cost
        if self.cost == 0:
            cost += self.instance.deployment_cost
        
        cost += self.instance.violation_cost_customer * sum(
            max(0, self.departure_times[idx] + added_charge_time - self.instance.deadlines[node]) \
            for idx, node in enumerate(route[prev_charger:idx-1])
            if node in self.instance.customer_ids # i.e. is customer. Handle lockers!
        )
        cost += self.instance.violation_cost_customer * sum(
            max(0, self.departure_times[idx] + delay - self.instance.deadlines[node])
            for idx, node in enumerate(route[idx:]):
            if node in self.instance.customer_ids
        )
        cost += (self.departure_times[-1] + delay - self.instance.deadlines[0]) * self.instance.violation_cost_depot
        return cost
        

    def _trip_idx(self, idx:int):
        begin = idx - 1
        end = idx
        while self.route[end] != 0:
            end += 1
        while self.route[begin] != 0:
            begin -= 1
        return begin, end
    
    def insert_customer(self, node: int, idx=-1):
        added_distance = self.distance(self.route[idx-1], node) +\
            self.distance(node, self.route[idx]) -\
            self.distance(self.route[idx-1], self.route[idx])

        added_charge = added_distance * self.instance.discharge_rate
        prev_charger = self._prev_charger_idx(idx)
        self.recharge_quantity[prev_charger] += added_charge
        if added_charge + prev_recharge_quantity < 0:
            added_charge_time = 0
        else:
            added_charge_time = (added_charge + min(prev_recharge_quantity, 0)) / self.instance.discharge_rate

        departure_time = self.departure_times[idx-1] +\
            self.distance(self.route[idx-1], node) / self.instance.speed + \
            added_charge_time + self.instance.service_times[node]

        delay = departure_time + self.distance(node, self.route[idx]) / self.instance.speed +\
            self.instance.service_times[self.route[idx]] - self.departure_times[idx]

        for idx, node in enumerate(route[prev_charger:idx-1]):
            self.departure_times[idx] += added_charge_time
        for idx, node in enumerate(route[idx:]):
            self.departure_times[idx] += delay

        if idx => len(self.route):
            self.route.extend([0, node, 0])
        self.route.insert(idx, node)
        self.route_cost += self.insert_cost(idx, node)
        self.load.insert(idx, self.load[idx-1])
        tidx = self._trip_idx(idx)
        for i in range(tidx[0], tidx[1]):
            self.load[i] += self.instance.demands[node]

            
    def remove_customer(self, node):
        idx = self.route.index(node)
        arc1 = (self.route[idx - 1], node)
        arc2 = (node, self.route[idx + 1])
        if node in self.instance.demands:
            self.load[trip] -= self.instance.demands[node]
        self.total_distance -= self.instance.distances.loc[arc1[0], arc1[1]]
        self.total_distance -= self.instance.distances.loc[arc2[0], arc2[1]]
        self.total_distance += self.instance.distances.loc[arc1[0], arc2[1]]
        self.recharge_quantities[trip].pop(idx)
        self.route[trip].remove(node)
        
    def minimize_recharge_quantities(self):
        charge = self.instance.initial_charge[self.ID]
        for trip_idx, trip in enumerate(self.route):
            prev_charge_idx = 0
            prev_node = trip[0]
            distance = 0
            for idx, node in enumerate(trip[1:]):
                distance += self.instance.distances.loc[prev_node, node]
                if node in self.instance.charger_ids:
                    charge_needed = distance * self.instance.discharge_rate
                    recharge = max(0, charge_needed - charge)
                    charge = charge + recharge - charge_needed
                    # charge_time = charge_needed / self.instance.recharge_rate
                    self.recharge_quantities[trip_idx][prev_charge_idx] = recharge
                    prev_charge_idx = idx + 1
                    distance = 0
                prev_node = node

    def departure_times(self):
        departure_times = []
        for i, trip in enumerate(self.route):
            dti = [self.recharge_quantities[i][0] / self.instance.recharge_rate]
            prev_node = trip[0]
            for j, node in enumerate(trip[1:]):
                time = dti[-1]
                # add travel time
                time += self.instance.distances.loc[prev_node, node] / self.instance.speed
                # add service time
                if node in self.instance.service_times:
                    time += self.instance.service_times[node]
                time += self.recharge_quantities[i][j+1] / self.instance.recharge_rate
                dti.append(time)
            departure_times.append(dti)
        return departure_times

    def print(self):
        def format_list(lst):
            return "[" + ", ".join(f"{x:.2f}" if isinstance(x, (float, np.float64, np.float32)) else str(x) for x in lst) + "]"

        print(f"Vehicle {self.ID}:")
        print(f"Route:".ljust(20), [format_list(trip) for trip in self.route])
        print(f"Recharge Quantities:".ljust(20), [format_list(rq) for rq in self.recharge_quantities])
        print(f"Departure Times:".ljust(20), [format_list(dt) for dt in self.departure_times()])
        print(f"Loads:".ljust(20), format_list(self.load))
        print(f"Total Distance:".ljust(20), f"{self.total_distance:.2f}")
        print()

    def __repr__(self):
        return f"Vehicle {self.ID} | Route: {self.route} | Load: {self.load} | Distance: {self.total_distance:.2f}"
