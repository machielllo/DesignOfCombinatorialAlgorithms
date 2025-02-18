from math import e
from instance import Instance
from copy import deepcopy

class Vehicle:
    def __init__(
        self, initial_charge,
        route: list = None,
        load: list = None,   
        charge_times: list = None          
    ):
        self.charge = initial_charge
        if route is None:
            self.route = [[0, 0]]
        else:
            self.route = route
        if load is None:
            self.load = [0]
        else:
            self.load = load
        if charge_times is None:
            self.charge_times = [[0, 0]]
        else:
            self.charge_times = charge_times

    def copy(self):
        return Vehicle(
            self.charge,
            route=self.route.deepcopy(),
            load=self.load.copy(),
            charge_times=self.charge_times.deepcopy()
        )

    def next_empty_trip(self):
        for idx, trip in enumerate(self.routes):
            if trip == [0, 0]:
                return idx
        self.routes.append([0, 0])
        self.load.append(0)
        return idx + 1
