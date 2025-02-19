from instance import Instance
from vehicle import Vehicle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Solution:
    def __init__(self, instance: Instance,
                 vehicles: dict = None,
                 customer_assignment: dict = None,
                 cost: float = None,
                 name: str = None,
                 valid: bool = False,
                 request_list: list = []):
        self.instance = instance
        if vehicles is None:
            self.vehicles = {vid: Vehicle(instance, vid) for vid in instance.vehicle_ids}
        else:
            self.vehicles = vehicles
        if customer_assignment is None:
            # (vehicle_id, trip_idx, locker_id)
            self.customer_assignment = {cid: None for cid in instance.customer_ids}
        else:
            self.customer_assignment = customer_assignment
        if cost is None:
            self.cost = np.inf
        else:    
            self.cost = cost
        if name is None:
            self.name = ""
        else:
            self.name = name
        self.valid = valid
        self.request_list = request_list
    
    def valid(self) -> bool:
        pass
        
    def locker_cost(self) -> float:
        pass
    
    def copy(self):
        return Solution(
            self.instance,
            vehicles={vid: v.copy() for vid, v in self.vehicles.items()},
            customer_assignment=self.customer_assignment.copy(),
            cost=self.cost,
            name=self.name,
            valid=self.valid,
            request_list=self.request_list.copy()
        )
        
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

            f.write(self.valid)
            if annotations:
                f.write(" // 1 iff we believe this solution is feasible, otherwise 0")
            f.write("\n")

            f.write(f"{self.cost:.3f}")
            if annotations:
                f.write(" // Total objective (real)")
            f.write("\n")

            f.write(f"{self.locker_cost():.3f}")
            if annotations:
                f.write(" // Locker open cost (real)")
            f.write("\n")

            f.write(f"{self.deployment_cost:.3f}")
            if annotations:
                f.write(" // Vehicle deploy cost (real)")
            f.write("\n")

            f.write(f"{self.travel_cost:.3f}")
            if annotations:
                f.write(" // Distance cost (real)")
            f.write("\n")

            f.write(f"{self.violation_cost_customer:.3f}")
            if annotations:
                f.write(" // Lateness penalty at customers (real)")
            f.write("\n")

            f.write(f"{self.violation_cost_depot:.3f}")
            if annotations:
                f.write(" // Lateness penalty at depot (real)")
            f.write("\n")

            locker_indicators = []
            for cid in self.instance.customer_ids:
                locker_indicators.append(str(self.customer_assignment.get(cid, 0)))
            f.write(", ".join(locker_indicators))
            if annotations:
                f.write(
                    " // Indicator of locker delivery for every customer 1, ..., n (0 if home delivery; locker's node ID, if locker delivery; empty line if n = 0)")
            f.write("\n")


            for vid in sorted(self.vehicles.keys()):
                vehicle = self.vehicles[vid]

                route_line = f"{vid}, " + ", ".join(str(stop) for stop in vehicle.route)
                f.write(route_line)
                if annotations:
                    f.write(f" // Route vehicle {vid}")
                f.write("\n")

                cq_line = f"{vid}, " + ", ".join(f"{q:.3f}" for q in vehicle.charge_quantities)
                f.write(cq_line)
                if annotations:
                    f.write(f" // Charge quantities vehicle {vid}")
                f.write("\n")

                ut_line = f"{vid}, " + ", ".join(f"{ut:.6f}" for ut in vehicle.unloading_times)
                f.write(ut_line)
                if annotations:
                    f.write(f" // Unloading completion time vehicle {vid}")
                f.write("\n")
                
    def plot(self, ax=None):
        "Plot the solution"
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 12))
        depot = self.instance.locations[self.instance.depot_id]
        ax.scatter(depot[0], depot[1], marker='s', color='blue')
        customers_x = [self.instance.locations[cid][0] for cid in self.instance.customer_ids]
        customers_y = [self.instance.locations[cid][1] for cid in self.instance.customer_ids]
        ax.scatter(customers_x, customers_y, marker='x', color='blue')
        chargers_x = [self.instance.locations[cid][0] for cid in self.instance.charger_ids]
        chargers_y = [self.instance.locations[cid][1] for cid in self.instance.charger_ids]
        ax.scatter(chargers_x, chargers_y, marker='P', color='yellow')
        lockers_x = [self.instance.locations[cid][0] for cid in self.instance.locker_ids]
        lockers_y = [self.instance.locations[cid][1] for cid in self.instance.locker_ids]
        ax.scatter(lockers_x, lockers_y, marker='^', color='red')
        for x, y in zip(lockers_x, lockers_y):
            circle = patches.Circle((x, y), self.instance.locker_radius, edgecolor='red', facecolor='none', linewidth=2)
            ax.add_patch(circle)
        max_distance = self.instance.battery_capacity / self.instance.discharge_rate
        for x, y in zip(chargers_x, lockers_y):
            circle = patches.Circle((x, y), max_distance, edgecolor='none', facecolor='paleturquoise', linewidth=2, alpha=0.5)
            ax.add_patch(circle)
        circle = patches.Circle((depot[0], depot[1]), max_distance, edgecolor='none', facecolor='paleturquoise', linewidth=2, alpha=0.2)
        ax.add_patch(circle)

        for v in self.vehicles.values():
            for trip in v.route:
                locations = [self.instance.locations[ID] for ID in trip]
                x, y = zip(*locations)
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
        fig.show()

    def total_cost(self) -> float:
        return self.distance_based_cost() + self.deployment_cost() + self.penalty_cost()

    def distance_based_cost(self) -> float:
        travel_cost = 0
        for v in self.vehicles.values():
            travel_cost += (self.instance.travel_cost * v.total_distance)

        return travel_cost

    def deployment_cost(self) -> float:
        deployed_vehicles = 0
        for v in self.vehicles.values():
            if v.total_distance != 0:
                deployed_vehicles += 1


        return self.instance.deployment_cost * deployed_vehicles

    def penalty_cost(self) -> float:
        "calculate the cost for deadline penalties"
        depot_penalty = 0
        customer_penalty = 0
        for v in self.vehicles.values():
            departure_times = v.departure_times()
            depot_penalty += self.instance.violation_cost_depot * max(
                0, departure_times[-1] - self.instance.deadlines[self.instance.depot_id]
            )
            customer_penalty += self.instance.violation_cost_customer * max(
                0, departure_times[-1] - self.instance.deadlines[self.instance.customer_id]
            )

            
            
    # def insert_cost(self, node_id: int, vid: int, trip: int, index: int):
    #     if self.vehicles[vid].load[trip] + self.instance.demands[node_id] > \
    #        self.instance.volume_capacity:
    #         return np.inf
        
    #     arc = self.vehicles[vid].route[trip][index-1], self.vehicles[vid].route[trip][index]
    #     delta_distance = -self.instance.distances.loc[arc[0], arc[1]]
    #     delta_distance += self.instance.distances.loc[arc[0], node_id]
    #     delta_distance += self.instance.distances.loc[node_id, arc[0]]
    #     cost = delta_distance * self.instance.travel_cost
    #     if self.vehicles[vid].total_distance == 0:
    #         cost += self.instance.deployment_cost
        
