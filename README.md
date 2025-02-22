# DesignOfCombinatorialAlgorithms
DCA Course RUG 2025 

## Instance
read

## Solution
write
draw
insert
remove
add_to_locker
remove_from_locker
cost_total
next_empty_trip
feasible

usefull:
 - _demand / _distance / etc
 - _cost_locker / _cost_distance / etc
 - ``__deepcopy__`` / ``__str__`` / etc


maybe:
``extend``
intermediate cost saving?

probably:
rework ``_check_X``
e.g. after removing stuff, need some way to check if a trip charge is OK


## Construct
Why does 973 go to an empty locker?

Maybe make simpler, no nearest-neighbor, just one per trip:
 - while unassigned:
 - n = unassigned.pop()
 - path = shortest_path(tree, 0, n, instance)
 - if path[-2] not in instance.locker_ids:
 - solution.insert(path[1:] + path[-2:1:-1]) (?)
 - else: assign musts (and extras) to locker
 - remove locker from tree
 - solution.insert(path[1:-1] + path[-3:1:-1]) (?)

## TODO: ALNS
copy alns

should mostly work

## TODO: TESTING 

