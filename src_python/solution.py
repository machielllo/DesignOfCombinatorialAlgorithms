from instance import Instance
from vehicle import Vehicle
import numpy as np

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
            self.vehicles = {vid: Vehicle(instance.inital_charge[vid]) for vid in instance.vehicle_ids}
        else:
            self.vehicles = vehicles
        if customer_assignment is None:
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
        
    def write(self, file_path: str):
        with open(file_path, 'w') as f:
            f.write(self.instance.instance_id + '\n')
            f.write(self.name + '\n')
            f.write(self.valid() + '\n')
            f.write(f"{self.cost:.3f}\n")
            
