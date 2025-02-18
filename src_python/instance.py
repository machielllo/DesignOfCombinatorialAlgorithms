from itertools import combinations
import numpy as np
import pandas as pd


class Instance:
    def __init__(self, file_path: str):
        self.read_instance(file_path)
        loc_values = list(self.locations.values())
        node_ids = list(self.locations.keys())
        self.distances = pd.DataFrame(
            np.linalg.norm(np.array(loc_values)[:, np.newaxis] - np.array(loc_values), axis=2),
            index=node_ids, columns=node_ids
        )

        
    def read_instance(self, file_path: str):
        with open(file_path, 'r') as f:
            self.instance_id = int(f.readline())
            f.readline()        # skip empty line
            self.num_customers = int(f.readline())
            self.num_chargers = int(f.readline())
            self.num_lockers = int(f.readline())
            self.num_vehicles = int(f.readline())
            self.speed = float(f.readline())
            self.volume_capacity = int(f.readline())
            self.battery_capacity = float(f.readline()) # float?
            self.discharge_rate = float(f.readline())
            self.recharge_rate = float(f.readline())
            self.locker_radius = float(f.readline())
            self.locker_cost = float(f.readline())
            self.deployment_cost = float(f.readline())
            self.travel_cost = float(f.readline())
            self.violation_cost_customer = float(f.readline())
            self.violation_cost_depot = float(f.readline())
            
            self.vehicle_ids = []
            self.inital_charge = dict()
            for i in range(self.num_vehicles):
                vid, charge = f.readline().split(',')
                self.vehicle_ids.append(int(vid))
                self.inital_charge[int(vid)] = float(charge)
            
            self.customer_ids = []
            self.locker_ids = []
            self.charger_ids = []
            self.locations = {}
            self.demands = {}
            self.service_times = {}
            self.deadlines = {}
    
            node_id, x, y, deadline = f.readline().split(',')
            self.depot_id = int(node_id)
            self.locations[int(node_id)] = (float(x), float(y))
            self.deadlines[int(node_id)] = float(deadline)

            for i in range(self.num_customers):
                node_id, x, y, service_time, deadline, demand = f.readline().split(',')
                self.customer_ids.append(int(node_id))
                self.locations[int(node_id)] = (float(x), float(y))
                self.demands[int(node_id)] = float(demand)
                self.service_times[int(node_id)] = float(service_time)
                self.deadlines[int(node_id)] = float(deadline)
                                
            for i in range(self.num_chargers):
                node_id, x, y = f.readline().split(',')
                self.charger_ids.append(int(node_id))
                self.locations[int(node_id)] = (float(x), float(y))
                                
            for i in range(self.num_lockers):
                node_id, x, y, service_time = f.readline().split(',')
                self.locker_ids.append(int(node_id))
                self.locations[int(node_id)] = (float(x), float(y))
                self.service_times[int(node_id)] = float(service_time)

        def reachable_return(node_id, start=self.depot_id, charge=self.battery_capacity):
            total_distance = distance[start, node_id] + distance[node_id, self.depot_id]
            if total_distance * self.discharge_rate < charge:
                return True
            else return False
            
