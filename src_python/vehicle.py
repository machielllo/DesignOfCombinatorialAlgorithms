from math import e
from instance import Instance
from copy import deepcopy

class Vehicle:
    def __init__(
        self,
        instance: Instance,
        route: list = None,
        load: list = None,
        charge_times: list = None          
        total_distance: float = 0,
    ):
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
        if charge_times is None:
            self.charge_times = [[0, 0]]
        else:
            self.charge_times = charge_times

    def copy(self):
        return Vehicle(
            instance=self.instance,
            route=self.route.deepcopy(),
            load=self.load.copy(),
            distance=self.total_distance,
            charge_times=self.charge_times.deepcopy()
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
        self.load[trip] += self.instance.demand[node_id]
        self.distance -= self.instance.distances.loc[*deleted_arc]
        self.distance += self.instance.distances.loc[deleted_arc[0], node_id]
        self.distance += self.instance.distances.loc[node_id, deleted_arc[1]]
        self.charge.insert(position, charge)

    def minimize_charge_times(self):
        pass
        
    def __repr__(self):
        full_str = ""
        for trip in self.route:
            full_str += trip.__str__()
        return full_str
