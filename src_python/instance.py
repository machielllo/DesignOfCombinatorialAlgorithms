from itertools import combinations
import numpy as np
import pandas as pd
import heapq

class Instance:
    def __init__(self, file_path: str):
        self.read(file_path)
        loc_values = list(self.locations.values())
        node_ids = list(self.locations.keys())
        self.distances = pd.DataFrame(
            np.linalg.norm(np.array(loc_values)[:, np.newaxis] - np.array(loc_values), axis=2),
            index=node_ids, columns=node_ids
        )
        self._dijkstra()

        
    def read(self, file_path: str):
        with open(file_path, 'r') as f:
            self.instance_id = int(f.readline())
            self.instance_name = f.readline().strip()
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
            self.initial_charge = dict()
            for i in range(self.num_vehicles):
                vid, charge = f.readline().split(',')
                self.vehicle_ids.append(int(vid))
                self.initial_charge[int(vid)] = float(charge)
            
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

    # def find_charge_path(self, from_id: int, to_id: int, charge=None) -> list[int]:
    #     "return a list of charging stations along the way"
    #     if charge is None:
    #         charge = self.battery_capacity
    #     intermediate_chargers = [
    #         chid for chid in self.charger_ids if
    #         self.distances.loc[chid, to_id] < self.distances.loc[from_id, to_id] and
    #         self.distances.loc[chid, from_id] < self.distances.loc[from_id, to_id]
    #     ]
        
    
                
    def reachable_return(self, node_id, start=None, charge=None):
        if start is None:
            start = self.depot_id
        if charge is None:
            charge = self.battery_capacity
        total_distance = self.distances.loc[start, node_id] + self.distances.loc[node_id, self.depot_id]
        if total_distance * self.discharge_rate < charge:
            return True
        else:
            return False
            

    # def reduced_charge_graph(self):
    #     max_distance = self.battery_capacity / self.discharge_rate
    #     graph = self.distances.copy()
    #     for i in self.customer_ids:
    #         for j in self.customer_ids:
    #             graph.loc[i, j] = np.inf
    #     for col in graph.columns:
    #         if col in self.locker_ids:
    #             graph[col] = graph[col].apply(lambda x: np.inf if x > self.locker_radius)
    #         else:
    #             graph[col] = graph[col].apply(lambda x: np.inf if x > max_distance)
    #     np.fill_diagonal(graph, np.inf)
    #     return graph
        
    
    def _dijkstra(self):
        max_distance = self.battery_capacity / self.discharge_rate
        graph = self.distances.copy()
        graph.loc[self.customer_ids] = np.inf
        graph.loc[self.locker_ids, self.locker_ids] = np.inf
        graph.loc[self.locker_ids, self.charger_ids] = np.inf
        graph.loc[self.locker_ids, self.depot_id] = np.inf
        np.fill_diagonal(graph.values, np.inf)
        graph.loc[self.locker_ids, self.customer_ids] = graph.loc[self.locker_ids, self.customer_ids].map(
            lambda x: np.inf if x > self.locker_radius else x
        )
        graph.loc[self.depot_id, self.locker_ids + self.customer_ids] = \
            graph.loc[self.depot_id, self.locker_ids + self.customer_ids].map(
                lambda x: np.inf if 2 * x > max_distance else x
            )
        graph.loc[self.depot_id, self.charger_ids] = \
            graph.loc[self.depot_id, self.charger_ids].map(
                lambda x: np.inf if x > max_distance else x
            )
        graph.loc[self.charger_ids, self.locker_ids + self.customer_ids] = \
            graph.loc[self.charger_ids, self.locker_ids + self.customer_ids].map(
                lambda x: np.inf if 2*x > max_distance else x
            )
        graph.loc[self.charger_ids, self.depot_id] = \
            graph.loc[self.charger_ids, self.depot_id].map(
                lambda x: np.inf if x > max_distance else x
            )
        graph.loc[self.charger_ids, self.charger_ids] = \
            graph.loc[self.charger_ids, self.charger_ids].map(
                lambda x: np.inf if x > max_distance else x
            )
        self.graph = graph
        n = len(graph)
        distances = {i: float('inf') for i in range(n)}
        distances[self.depot_id] = 0
        priority_queue = [(0, self.depot_id)]
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
        
    def shortest_capable_path(self, target):
        path = []
        while target is not None:
            path.append(target)
            target = self.dijkstra_predecessors[target]
        return path[::-1]
