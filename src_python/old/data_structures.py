from itertools import combinations
import numpy as np
import pandas as pd

ID = int


class Instance:
    def __init__(self, file_path):
        self.read_instance(file_path: str)

        np.linalg.norm()
        self.distances = pd.DataFrame()
        
        
    def read_instance(self, file_path: str):
        with open(file_path, 'r') as f:
            self.instance_id = int(f.readline())
            f.readline()        # skip empty line (?)
            self.num_customers = int(f.readline())
            self.num_chargers = int(f.readline())
            self.num_lockers = int(f.readline())
            self.num_vehicles = int(f.readline())
            self.speed = float(f.readline())
            self.volume_capacity = int(f.readline())
            self.battery_capacity = int(f.readline()) # float?
            self.discharge_rate = float(f.readline())
            self.recharge_rate = float(f.readline())
            self.locker_radius = float(f.readline())
            self.locker_cost = float(f.readline())
            self.deployment_cost = float(f.readline())
            self.travel_cost = float(f.readline())
            self.violation_cost_customer = float(f.readline())
            self.violation_cost_depot = float(f.readline())
            self.vehicles = dict()
            for i in range(self.num_vehicles):
                line = f.readline()
                vid, charge = line.split(',')
                self.vehicles[int(vid.strip())] = Vehicle(float(vid.strip()))
            
            self.nodes = dict()
            node_id, x, y, deadline = f.readline().split(',')
            self.nodes[node_id] = Depot(float(x), float(y), float(deadline))
            for i in range(self.num_customers):
                line = f.readline()
                node_id, x, y, service_time, deadline, demand = f.readline().split(',')
                self.customers[int(node_id)] = Customer(float(x), float(y), float(service_time), float(deadline), int(demand))
            for i in range(self.num_chargers):
                node_id, x, y = f.readline().split(',')
                self.nodes[int(node_id)] = Charger(float(x), float(y))
            for i in range(self.num_lockers):
                node_id, x, y, service_time = f.readline().split(',')
                self.nodes[int(node_id)] = Locker(float(x), float(y), float(service_time))
            # self.distances = np.linalg.norm(a - b for a, b in combinations(self.nodes.values()))

                
class Solution:
                
class Vehicle:
    def __init__(self, ID, charge):
        self.ID = ID
        self.charge = charge

        
