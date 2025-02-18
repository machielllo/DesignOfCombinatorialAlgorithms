from calendar import c
from itertools import cycle
from instance import Instance
from solution import Solution
from vehicle import Vehicle


def construction_heuristic(instance: Instance) -> Solution:
    "Construct an initial feasible solution"
    unassigned = set(instance.customer_ids)
    
    vehicles = {vid: Vehicle(instance) for vid in instance.vehicle_ids}
    vids = cycle(instance.vehicle_ids)
    customer_assignment = {cid: None for cid in instance.customer_ids}

    # for lid in instance.locker_ids:
    #     # Can the locker even be reached without charging?
    #     if not instance.reachable_return(lid):
    #         continue
    #     vid = next(vids)
    #     vehicle = vehicles[vid]
    #     assigned, load = initial_locker_assignment(lid, instance, unassigned)
    #     if len(assigned) == 0:
    #         continue
        
    #     for cid in assigned:
    #         customer_assignment[cid] = (vid, None, lid)
    #         unassigned.remove(cid)
    #     # What if I have more lockers than vehicles?
    #     trip = vehicle.next_empty_trip()
    #     vehicle.insert(node_id=lid, trip=trip)
    #     vehicle.load[trip] = load
    #     # vehicle.distance = 2 * instance.distance[lid, instance.depot_id] # ?
    
    while unassigned:
        vid = next(vids)
        vehicle = vehicles[vid]
        trip = vehicle.next_empty_trip()
        
        nn = min(unassigned, key=lambda x: instance.distances.loc[instance.depot_id, x])

        if not instance.reachable_return(nn):
            path = instance.shortest_capable_path(nn)
            if path[-2] in instance.locker_ids:
                lid = path[-2]
                path = path[:-1] + path[:-1][::-1]
                customer_assignment[nn] = (vid, trip, lid)
            else:
                path = path + path[:-1][::-1]
                customer_assignment[nn] = (vid, trip, 0)
            vehicle.route[trip] = path
            vehicle.load[trip] = instance.demands[nn]
            unassigned.remove(nn)
            # print(path, '\nTo Do')
            
            
        distance = instance.distances.loc[instance.depot_id, nn]
        charge_cost = distance * instance.discharge_rate
        load = instance.demands[nn]
        prev = instance.depot_id
        while load <= instance.volume_capacity and \
              instance.reachable_return(nn, prev, instance.battery_capacity - charge_cost):
            vehicle.insert(node_id=nn, trip=trip)
            unassigned.remove(nn)
            customer_assignment[nn] = (vid, trip, 0)
            prev = nn
            nn = min(unassigned, key=lambda x: instance.distances.loc[instance.depot_id, x])
            distance = instance.distances.loc[prev, nn]
            charge_cost += distance * instance.discharge_rate
            load += instance.demands[nn]
            
        vehicle.load[trip] = load
    
    return Solution(instance, vehicles=vehicles, customer_assignment=customer_assignment,
                    valid=True, name="Construction Heuristic")


def initial_locker_assignment(locker_id: int, instance: Instance, unassigned) -> list[int]:
    "The customers furthers away from the depot, that can be assigned to a locker,\
    until the max capacity is reached"
    customers_near_locker = [cid for cid in unassigned if instance.distances.loc[locker_id, cid] <= instance.locker_radius]
    customers_near_locker.sort(key=lambda x: instance.distances.loc[x, instance.depot_id])
    assigned_customers = []
    if len(customers_near_locker) == 0:
        return [], 0
    idx = 0
    load = instance.demands[customers_near_locker[idx]]
    while load < instance.volume_capacity and idx < len(customers_near_locker) - 1:
        assigned_customers.append(customers_near_locker[idx])
        idx += 1
        load += instance.demands[customers_near_locker[idx]]
    return assigned_customers, load



