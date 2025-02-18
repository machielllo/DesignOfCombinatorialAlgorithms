from instance import Instance
from copy import deepcopy
import numpy as np

class Vehicle:
    def __init__(
        self,
        instance: Instance,
        ID: int,
        route: list = None,
        load: list = None,
        recharge_quantities: list = None, # drop!
        total_distance: float = 0,
    ):
        self.instance = instance
        self.ID = ID
        if route is None:
            self.route = [[0, 0]]
        else:
            self.route = route
        if load is None:
            self.load = [0]
        else:
            self.load = load
        if total_distance is None:
            self.total_distance = 0
        else:
            self.total_distance = total_distance
        if recharge_quantities is None:
            self.recharge_quantities = [[0, 0]]
        else:
            self.recharge_quantities = recharge_quantities
            
    def copy(self):
        return Vehicle(
            instance=self.instance,
            ID=self.ID,
            route=self.route.deepcopy(),
            load=self.load.copy(),
            total_distance=self.total_distance,
            recharge_quantities=self.recharge_quantities.deepcopy()
        )

    def next_empty_trip(self):
        for idx, trip in enumerate(self.route):
            if trip == [0, 0]:
                return idx
        self.route.append([0, 0])
        self.load.append(0)
        return idx + 1

    def insert(self, node_id: int, trip: int, position=-1, charge=0):
        deleted_arc = self.route[trip][position - 1], self.route[trip][position]
        self.route[trip].insert(position, node_id)
        if node_id in self.instance.demands:
            self.load[trip] += self.instance.demands[node_id]
        self.total_distance -= self.instance.distances.loc[*deleted_arc]
        self.total_distance += self.instance.distances.loc[deleted_arc[0], node_id]
        self.total_distance += self.instance.distances.loc[node_id, deleted_arc[1]]
        self.recharge_quantities[trip].insert(position, charge)

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
