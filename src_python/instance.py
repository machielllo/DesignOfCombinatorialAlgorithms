from itertools import combinations
import numpy as np
import pandas as pd
import heapq

ID = int

# This class is used to represent the instances that we receive from the lecturers.
class Instance:
    # The constructor to initialize an Instance object's attributes:
    def __init__(self, file_path: str):
        self.read(file_path) # Use the read function defined below.
        loc_values = list(self.location.values())
        node_ids = list(self.location.keys())
        # We create a matrix of the distance between different nodes.
        self.distance = pd.DataFrame(
            np.linalg.norm(np.array(loc_values)[:, np.newaxis] - np.array(loc_values), axis=2),
            index=node_ids, columns=node_ids
        )
        self.travel_time = self.distance / self.speed
        self.charge_cost = self.distance / self.rate_discharge
        self._dijkstra()
        
    def read(self, file_path: str):
        with open(file_path, 'r') as f:
            self.instance_id = int(f.readline())
            self.instance_name = f.readline().strip()
            self.num_customers = int(f.readline())
            self.num_chargers = int(f.readline())
            self.num_lockers = int(f.readline())
            self.num_vehicles = int(f.readline())
            self.num_nodes = self.num_customers + self.num_chargers + self.num_lockers + 1
            self.speed = float(f.readline())
            self.capacity_volume = int(f.readline())
            self.capacity_battery = float(f.readline()) # float?
            self.rate_discharge = float(f.readline())
            self.rate_recharge = float(f.readline())
            self.locker_radius = float(f.readline())
            self.cost_locker = float(f.readline())
            self.cost_deployment = float(f.readline())
            self.cost_distance = float(f.readline())
            self.cost_penalty_customer = float(f.readline())
            self.cost_penalty_depot = float(f.readline())
            
            # self.vehicle_ids = [] # ... always 1 : num_vehicles
            self.initial_charge = []
            for i in range(self.num_vehicles):
                vid, charge = f.readline().split(',')
                # self.vehicle_ids.append(int(vid))
                self.initial_charge.append(float(charge))
            
            self.customer_ids = set()
            self.locker_ids = set()
            self.charger_ids = set()
            self.location = {}
            self.demand = {}
            self.service_time = {}
            self.deadline = {}
    
            node, x, y, deadline = f.readline().split(',')
            if int(node) != 0:
                raise ValueError("Hold up! The depot is not 0!")
            self.location[0] = (float(x), float(y))
            self.deadline[0] = float(deadline)

            for i in range(self.num_customers):
                node, x, y, service_time, deadline, demand = f.readline().split(',')
                self.customer_ids.add(int(node))
                self.location[int(node)] = (float(x), float(y))
                self.demand[int(node)] = int(demand)
                self.service_time[int(node)] = float(service_time)
                self.deadline[int(node)] = float(deadline)
                                
            for i in range(self.num_chargers):
                node, x, y = f.readline().split(',')
                self.charger_ids.add(int(node))
                self.location[int(node)] = (float(x), float(y))
                                
            for i in range(self.num_lockers):
                node, x, y, service_time = f.readline().split(',')
                self.locker_ids.add(int(node))
                self.location[int(node)] = (float(x), float(y))
                self.service_time[int(node)] = float(service_time)

            self.chargable_ids = self.locker_ids | {0}    
                
    def reachable_return(self, node: ID, start: ID=None, charge=None):
        if start is None:
            start = self.depot_id
        if charge is None:
            charge = self.capacity_battery
        total_distance = self.distance.loc[start, node] + self.distance.loc[node, 0]
        if total_distance * self.rate_discharge <= charge:
            return True
        else:
            return False

    
    def _dijkstra(self):
        max_distance = self.capacity_battery / self.rate_discharge
        graph = self.distance.copy()
        np.fill_diagonal(graph.values, np.inf)
        graph.loc[list(self.customer_ids)] = np.inf
        graph.loc[list(self.locker_ids), list(self.locker_ids)] = np.inf
        graph.loc[list(self.locker_ids), list(self.chargable_ids)] = np.inf
        graph.loc[list(self.locker_ids), list(self.customer_ids)] = \
            graph.loc[list(self.locker_ids), list(self.customer_ids)].map(
            lambda x: np.inf if x > self.locker_radius else x
        )
        graph.loc[list(self.chargable_ids), list(self.locker_ids | self.customer_ids)] = \
            graph.loc[list(self.chargable_ids), list(self.locker_ids | self.customer_ids)].map(
                lambda x: np.inf if 2 * x > max_distance else x
            )
        graph.loc[list(self.chargable_ids), list(self.chargable_ids)] = \
            graph.loc[list(self.chargable_ids), list(self.chargable_ids)].map(
                lambda x: np.inf if x > max_distance else x
            )
        # self.graph = graph
        n = len(graph)
        distances = {i: float('inf') for i in range(n)}
        distances[0] = 0
        priority_queue = [(0, 0)]
        predecessors = {i: None for i in range(n)}

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            if current_distance > distances[current_node]:
                continue
            for neighbor, weight in enumerate(graph.iloc[current_node]):
                if weight != float('inf') and neighbor != current_node:
                    distance = current_distance + weight
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        predecessors[neighbor] = current_node
                        heapq.heappush(priority_queue, (distance, neighbor))

        self.dijkstra_distances = distances
        self.dijkstra_predecessors = predecessors
        
    def shortest_capable_path(self, node: ID):
        "From depot to node, so that the battery capacity is not violated"
        path = []
        while target is not None:
            path.append(target)
            target = self.dijkstra_predecessors[target]
        return path[::-1]

    def __repr__(self):
        return f"Instance({self.instance_id})"
