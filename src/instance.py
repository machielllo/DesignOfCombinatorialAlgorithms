from itertools import combinations
import numpy as np
import pandas as pd

ID = int


# This class is used to represent the instances that we receive from the lecturers.
# It contains all necessary data that does not change
# It can read the data from a .inst file
# TODO: generate instances ourself and write them to a .inst file
class Instance:
    # The constructor to initialize an Instance by reading a .inst file:
    def __init__(self, file_path: str):
        self.read(file_path)  # Use the read function defined below.
        loc_values = list(self.location.values())
        node_ids = list(self.location.keys())
        # We create a matrix of the distance between different nodes.
        self.distance = pd.DataFrame(
            np.linalg.norm(
                np.array(loc_values)[:, np.newaxis] - np.array(loc_values), axis=2
            ),
            index=node_ids,
            columns=node_ids,
        )
        # These only need to be calculated once
        self.travel_time = self.distance / self.speed
        self.charge_required = self.distance * self.rate_discharge

    def read(self, file_path: str):
        with open(file_path, "r") as f:
            self.instance_id = int(f.readline())
            self.instance_name = f.readline().strip()
            self.num_customers = int(f.readline())
            self.num_chargers = int(f.readline())
            self.num_lockers = int(f.readline())
            self.num_vehicles = int(f.readline())
            self.num_nodes = (
                self.num_customers + self.num_chargers + self.num_lockers + 1
            )
            self.speed = float(f.readline())
            self.capacity_volume = int(f.readline())
            self.capacity_battery = float(f.readline())  # float?
            self.rate_discharge = float(f.readline())
            self.rate_recharge = float(f.readline())
            self.radius_locker = float(f.readline())
            self.radius_chargable = self.capacity_battery / self.rate_discharge
            self.cost_locker = float(f.readline())
            self.cost_deployment = float(f.readline())
            self.cost_distance = float(f.readline())
            self.cost_penalty_customer = float(f.readline())
            self.cost_penalty_depot = float(f.readline())

            # self.vehicle_ids = [] # ... always [1, ..., num_vehicles]
            # we'll just use [0, ..., num_vehicles), and print them with vid + 1
            self.initial_charge = []
            for i in range(self.num_vehicles):
                vid, charge = f.readline().split(",")
                # self.vehicle_ids.append(int(vid))
                self.initial_charge.append(float(charge))

            # The sets are usefull for checking what type a node is
            self.customer_ids = set()
            self.locker_ids = set()
            self.charger_ids = set()
            # Relevant data. Make it default_dict? i.e. return 0 if key not in?
            self.location = {}
            self.demand = {}
            self.service_time = {}
            self.deadline = {}

            node, x, y, deadline = f.readline().split(",")
            if int(node) != 0:
                raise ValueError("Hold up! The depot is not 0!")
            self.location[0] = (float(x), float(y))
            self.deadline[0] = float(deadline)

            for i in range(self.num_customers):
                node, x, y, service_time, deadline, demand = f.readline().split(",")
                self.customer_ids.add(int(node))
                self.location[int(node)] = (float(x), float(y))
                self.demand[int(node)] = int(demand)
                self.service_time[int(node)] = float(service_time)
                self.deadline[int(node)] = float(deadline)

            for i in range(self.num_chargers):
                node, x, y = f.readline().split(",")
                self.charger_ids.add(int(node))
                self.location[int(node)] = (float(x), float(y))

            for i in range(self.num_lockers):
                node, x, y, service_time = f.readline().split(",")
                self.locker_ids.add(int(node))
                self.location[int(node)] = (float(x), float(y))
                self.service_time[int(node)] = float(service_time)

            self.chargable_ids = self.charger_ids | {0}

    def __repr__(self):
        return f"Instance({self.instance_id})"
