from calendar import c
from itertools import cycle
from instance import Instance
from solution import Solution
from vehicle import Vehicle


def constuction_heuristic(instance: Instance) -> Solution:
    unassigned = set(instance.customer_ids)
    
    vehicles = {vid: Vehicle(instance.initial_charge[vid]) for vid in instance.vehicle_ids}
    vids = cycle(instance.vehicle_ids)
    
    customer_assignment = {cid: None for cid in instance.customer_ids}
    
    while unassigned:
        vehicle = vehicles[next(vids)]
        
        nearest_to_depot = min(unassigned, key=lambda x: instance.distances[instance.depot_id][x])
        distance = instance.distances[instance.depot_id][nearest_to_depot]
        charge_cost = distance / instance.discharge_rate
        extra_load = instance.demands[nearest_to_depot]
        
    
    return Solution(instance, vehicles=vehicles, customer_assignment=customer_assignment,
                    valid=True, name="Construction Heuristic")
