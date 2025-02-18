from calendar import c
from itertools import cycle
from instance import Instance
from solution import Solution
from vehicle import Vehicle




def construction_heuristic(instance: Instance) -> Solution:
    "Construct an initial feasible solution"
    unassigned = set(instance.customer_ids)
    
    vehicles = {vid: Vehicle(instance.initial_charge[vid]) for vid in instance.vehicle_ids}
    vids = cycle(instance.vehicle_ids)
    customer_assignment = {cid: None for cid in instance.customer_ids}

    for lid in instance.locker_ids:
        # Can the locker even be reached without charging?
        if not instance.reachable_return(lid):
            continue
        vehicle = vehicles[next(vids)]
        assigned, load = initial_locker_assignment(lid, instance, unassigned)
        
        for cid in assigned:
            customer_assignment[cid] = (vehicle.ID, None, lid)
            unassigned.remove(cid)
        # What if I have more lockers than vehicles?
        # vehicle.next_empty_trip
        trip = vehicle.next_empty_trip()
        vehicle.insert(node_id=lid, trip=trip, position=1)
        vehicle.load[trip] = load
        # vehicle.distance = 2 * instance.distance[lid, instance.depot_id] # ?
        
    
    while unassigned:
        vehicle = vehicles[next(vids)]
        trip = vehicle.next_empty_trip()
        
        nn = min(unassigned, key=lambda x: instance.distances[instance.depot_id][x])
        distance = instance.distances[instance.depot_id][nn]
        charge_cost = distance * instance.discharge_rate
        load = instance.demands[nn]
        prev = instance.depot_id
        while load <= instance.volume_capacity and instance.reachable(nn, prev, instance.battery_capacity - charge_cost):
            vehicle.append(node_id=nn, trip=trip)
            unassigned.remove(nn)
            prev = nn
            nn = min(unnassigned, key=lambda x: instance.distances[instance.depot_id][x])
            distance = instance.distances[instance.depot_id][nn]
            charge_cost = distance * instance.discharge_rate
            load = instance.demands[nn]
            prev = instance.depot_id
            
        vehicle.load[trip] = load
    
    return Solution(instance, vehicles=vehicles, customer_assignment=customer_assignment,
                    valid=True, name="Construction Heuristic")


def initial_locker_assignment(locker_id: int, instance: Instance, unassigned) -> list[int]:
    "The customers furthers away from the depot, that can be assigned to a locker,\
    until the max capacity is reached"
    customers_near_locker = [cid for cid in unassigned if distance[locker_id, cid] <= instance.locker_radius]
    customers_near_locker.sort(key=lambda x: distance[x, instance.depot_id])
    assigned_customers = []
    idx = 0
    load = instance.demands[customers_near_locker[idx]]
    while load < instance.volume_capacity:
        assigned_customers.append(customers_near_locker[idx])
        idx += 1
        load += instance.demands[customers_near_locker[idx]]
    return assigned_customers, load



