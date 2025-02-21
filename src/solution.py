import numpy as np
from instance import Instance
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import Counter
import copy

# For typing: make clear when something is a node
ID = int

# For indexing within the solution
class Index:
    """Index for routes, i.e. solution.routes[route][trip][index]
locker = 0   if not assigned to locker
locker = ID  if assigned to locker, (route, trip, index) are then meaningless
"""
    def __init__(self, route: int, trip: int, index: int, locker: ID):
        "Construct an Index"
        self.route = route
        self.trip = trip
        self.index = index
        self.locker = locker
        
    def __copy__(self):
        "Create a shallow copy of the Index"
        return Index(self.route, self.trip, self.index, self.locker)

    def __repr__(self):
        "Nice textual representation"
        return f"Index(route={self.route}, trip={self.trip}, index={self.index}, locker={self.locker})"


    
# The solution: writes to a .sol format.
# keeps route for each vehicle in self.routes (by index: 0, 1, ..., num_vehicles - 1)
# TODO: insert_new_empty_trip (automatic at self.insert() ?)
# TODO: remove redundant empty trip (automatic at self.remove() ?)
# keeps load for each trip in self.loads 
# insert and remove at Index
# calculate minimal charge quantity
# calculate departure times
# calculate costs
# smart intermediate savings (NEEDS TESTING)
# TODO: implement draw
# TODO: insert cost ? (maybe just do that in the operators)
class Solution:
    """Solution for problem"""
    def __init__(self, instance: Instance, name=""):
        self.instance = instance
        self.name = name
        
        self._v = range(instance.num_vehicles)        # is this genius or retarded?

        # All we need to keep track
        self.routes = [[[0, 0]] for _ in self._v]
        self.loads = [[0] for _ in self._v]

        # Keep indices of customers and lockers
        # None if not assigned
        self.assignments = {node: None for node in instance.customer_ids | instance.locker_ids}

        # Keep list of customers assigned to each locker
        self.lockers = {node: [] for node in instance.locker_ids}

        # These are only updated once needed and only for the routes that change
        self.distances = [0.0 for _ in self._v]
        self.departure_times = [[[0.0, 0.0]] for _ in self._v]
        self.charge_quantities = [[[0.0, 0.0]] for _ in self._v]

        # These will keep track of whether it needs to be recalculated for the route
        self._changed_distances = [False for _ in self._v]
        self._changed_departure_times = [False for _ in self._v]
        self._changed_charge_quantities = [False for _ in self._v]

        
    # TODO: add checks, should only be used in the end or debugging
    def feasible(self, verbose: bool = False) -> bool:
        "Check for a range of conditions, not exhaustive (yet)!"
        valid = True
        if not self._check_count(verbose):
            valid = False
        if not self._check_cycle(verbose):
            valid = False
        if not self._check_charge(verbose):
            valid = False
        if not self._check_count(verbose):
            valid = False
        return valid

    # Speaks for itself. The final call is important!
    def insert(self, index: Index, node: ID):
        "Insert node at index"
        self.routes[index.route][index.trip].insert(index.index, node)
        self.loads[index.route][index.trip] += self._demand(node)
        # All the customers/lockers that follow, now have their index increased by 1
        if node in self.assignments:
            self.assignments[node] = index
        for node2 in self.routes[index.route][index.trip][(index.index+1):]:
            if node2 in self.assignments:
                self.assignments[node2].index += 1
        self._route_changed(index.route)

    # Speaks for itself
    def remove(self, index: Index):
        "Remove node at index"
        node = self.routes[index.route][index.trip].pop(index.index)
        if node in self.assignments:
            self.assignments[node] = None
        for node2 in self.routes[index.route][index.trip][index.index:]:
            if node2 in self.assignments:
                self.assignments[node2].index -= 1
        self._route_changed(index.route)

    # May need some more checks
    def add_to_locker(self, locker: ID, customer: ID):
        "Add customer to locker"
        self.lockers[locker].append(customer)
        self.assignments[customer] = Index(0, 0, 0, locker)

        # If the locker is assigned to a trip, update the load
        index = self.assignments[locker]
        if index is not None:
            self.loads[index.route][index.trip] += self._demand(customer)

    def remove_from_locker(self, locker: ID, customer: ID):
        "Remove customer from locker"
        self.lockers[locker].remove(customer)
        self.assignments[customer] = None

        # If the locker is assigned to a trip, update the load
        index = self.assignments[locker]
        if index is not None:
            self.loads[index.route][index.trip] -= self._demand(customer)


    def get_index(self, node: ID) -> Index:
        "Return the index of node"
        # TODO: copy?
        index = self.assignments[node]
        return index
    
    # TODO [#C]: add annotations
    def write(self, file_path: str):
        "Write solution out as a .sol file"
        with open(file_path, 'w') as f:
            f.write(self.__str__())

    def cost_total(self) -> float:
        "Calculate total costs"
        costs = 0.0
        costs += self._cost_lockers()
        costs += self._cost_deployment()
        costs += self._cost_distance()
        costs += self._cost_penalty_customers()
        costs += self._cost_penalty_depot()
        return costs

    
    def draw(self, ax=None, file_out=None):
        """Draw the instance and solution."""
        if ax is None:
            fig, ax = plt.subplots()
            plot = True

        self._plot_instance(ax)
        for route in self._v:
            self._plot_route(ax, route)

        for locker in self.lockers:
            self._plot_locker(ax, locker)

        self._plot_empty(ax)
            
        if plot is True:
            if file_out is None:
                plt.show()
            else:
                plt.savefig(file_out)

    def next_empty_trip(self, route: int) -> int:
        for idx, trip in enumerate(self.routes[route]):
            if trip == [0, 0]:
                return idx
        self._add_empty_trip(route)
        return idx + 1
    
    ### The distances charge_quantity and departure time setters
    
    @property
    def distances(self):
        for route in self._v:
            if self._changed_distances[route]:
                self._distance_route(route)
        return self._distances

    @distances.setter
    def distances(self, value):
        self._distances = value

    def _distance_route(self, route: int):
        "Calculate the total distance of the route (again)"
        distance = 0.0
        for trip in self.routes[route]:
            node1 = 0
            for node2 in trip[1:]:
                distance += self._distance(node1, node2)
        self._distances[route] = distance
        self._changed_distances[route] = False

    @property
    def charge_quantities(self):
        for route in self._v:
            if self._changed_charge_quantities[route]:
                self._charge_quantities_route(route)
        return self._charge_quantities

    @charge_quantities.setter
    def charge_quantities(self, value):
        self._charge_quantities = value

    def _charge_quantities_route(self, route: int):
        """Calculate the charging quantities for the route.
Always charge as little as possible: so that you reach the next charging place.
May charge more than the battery capacity allows!
"""
        # The initial charge
        charge = self.instance.initial_charge[route]
        self._charge_quantities[route] = [[0.0] * len(trip) for trip in self.routes[route]]

        index = Index(route, 0, 0, 0)
        for trip in self.routes[route]:
            # Keep track of the last charging place index in trip
            prev_charge_idx = 0 
            node1 = 0
            charge_needed = 0.0
            for node2 in trip[1:]:
                index.index += 1
                charge_needed += self._charge_required(node1, node2)
                if node2 in self.instance.chargable_ids:
                    recharge = max(0, charge_needed - charge)
                    charge = charge + recharge - charge_needed
                    # So that now we can change the recharge quantity of the previous charging place
                    self._charge_quantities[route][index.trip][prev_charge_idx] = recharge
                    prev_charge_idx = index.index
                    charge_needed = 0.0
                node1 = node2
            index.trip += 1
            index.index = 0
        self._changed_charge_quantities[route] = False
        
    @property
    def departure_times(self):
        for route in self._v:
            if self._changed_departure_times[route]:
                self._departure_times_route(route)
        return self._departure_times

    @departure_times.setter
    def departure_times(self, value):
        self._departure_times = value

    def _departure_times_route(self, route: int):
        "(Re)calculate the departure times of the route"
        self._departure_times[route] = [[0.0]*len(trip) for trip in self.routes[route]]
        trip_idx = 0
        dt = 0.0
        for trip in self.routes[route]:
            dt += self.charge_quantities[route][trip_idx][0] / self.instance.rate_recharge
            self._departure_times[route][trip_idx][0] = dt 
            node1 = 0
            idx = 1
            for node2 in trip[1:]:
                dt += self._travel_time(node1, node2)
                dt += self._service_time(node2)
                dt += self.charge_quantities[route][trip_idx][idx] / self.instance.rate_recharge
                self._departure_times[route][trip_idx][idx] = dt
                idx += 1
            trip_idx += 1
        self._changed_departure_times[route] = False
                    
    def _route_changed(self, route):
        "A route is adjusted after inserting or removing a node"
        self._changed_distances[route] = True
        self._changed_departure_times[route] = True
        self._changed_charge_quantities[route] = True

    def _add_empty_trip(self, route):
        "Add an empty trip to the route"
        self.routes[route].append([0, 0])
        self.loads[route].append(0)
        self._route_changed(route)

    ### Partial Cost Functions
    def _cost_lockers(self) -> float:
        "Calculate the opening cost of the used lockers"
        cost = 0.0
        for v in self.lockers.values():
            if v:               # note: bool([]) is False
                cost += self.instance.cost_locker
        return cost

    def _cost_deployment(self) -> float:
        "Calculate the cost of deploying used vehicles"
        vu = 0
        # Is this the best way of checking it?
        for route in self._v:
            if self.distances[route] > 0:
                vu += 1
        return vu * self.instance.cost_deployment
    
    def _cost_distance(self) -> float:
        distance = sum(self.distances)
        return distance * self.instance.cost_distance

    # Save this too, i.e. for each route?
    def _cost_penalty_customers(self) -> float:
        "The penalty for missing the deadlines of customers"
        total = 0.0
        # iterate over each customer
        for customer in self.instance.customer_ids:
            index = self.assignments[customer]
            # if the customer is not assigned, continue
            if index is None:
                continue
            # even if the customer is in a locker, the index points to the locker
            t = self.departure_times[index.route][index.trip][index.index]
            total += max(0, t - self.instance.deadline[customer])
        return total * self.instance.cost_penalty_customer
        
    def _cost_penalty_depot(self) -> float:
        "The penalty for being late at the depot"
        total = 0.0
        for route in self._v:
            total += self.departure_times[route][-1][-1]
        return total * self.instance.cost_penalty_depot

    ### The feasibility checkers

    def _check_volume(self, verbose: bool) -> bool:
        "Check if capacity restrictions are violated"
        for route in self._v:
            for trip in range(len(route)):
                if self.loads[route][trip] > self.instance.capacity_volume:
                    verbose and print(f"Vehicle {route + 1} is overloaded on trip {trip}")
                    valid = False
        return valid
        ## Recalculate everything?
        # valid = True
        # for i, route in enumerate(self.routes):
        #     for j, trip in enumerate(route):
        #         total_demand = 0
        #         for node in trip:
        #             demand += self._demand(node)
        #         if total_demand > self.instance.capacity_volume:
        #             verbose and print(f"Vehicle {i + 1} is overloaded on trip {j}")
        #             valid = False
        # return valid

    def _check_charge(self, verbose: bool) -> bool:
        "Check if charge constraints are violated"
        valid = True
        index = Index(0, 0, 0, 0)
        for route in self.routes:
            charge = self.instance.initial_charge[index.route]
            for trip in route:
                charge += self.charge_quantities[index.route][index.trip][0]
                prev = 0
                for node in trip[1:]:
                    index.index += 1
                    charge -= self._charge_required(prev, node)
                    prev = node
                    charge += self.charge_quantities[index.route][index.trip][index.index]
                    if node not in self.instance.chargable_ids \
                       and self.charge_quantities[index.route][index.trip][index.index] > 0.01:
                        verbose and print(f"Vehicle {index.route + 1} gets charged at {node}")
                    if charge > self.instance.capacity_battery + 0.01:
                        verbose and print(f"Vehicle {index.route + 1} is overcharged at {node}")
                        valid = False
                    if charge < -0.01:
                        verbose and print(f"Vehicle {index.route + 1} is undercharged at {node}")
                        valid = False
                index.trip += 1
                index.index = 0
            index.trip = 0
            index.index = 0
            index.route += 1
        return valid
            
    def _check_cycle(self, verbose: bool) -> bool:
        "Check if we start and end at depot"
        valid = True
        for i, route in enumerate(self.routes):
            for j, trip in enumerate(route):
                if trip[0] != 0:
                    verbose and print(f"Vehicle {i + 1} does not start at depot on trip {j}")
                    valid = False
                if trip[-1] != 0:
                    verbose and print(f"Vehicle {i + 1} does not end at depot on trip {j}")
                    valid = False
        return valid

    def _check_count(self, verbose: bool) -> bool:
        "Check if customers and lockers are assigned once and if lockers are assigned when used"
        valid = True
        c = Counter()
        for route in self.routes:
            for trip in route:
                c.update(trip)
            
        for locker, customers in self.lockers.items():
            if customers:
                if c[locker] == 0:
                    verbose and print(f"Locker {locker} used but not assigned")
                    valid = False
                if c[locker] > 1:
                    verbose and print(f"Locker {locker} assigned multiple times")
                c.update(customers)
                
        for node in self.instance.customer_ids:
            if node not in c:
                verbose and print(f"Customer {node} not assigned")
                valid = False
            if c[node] > 1:
                verbose and print(f"Customer {node} assigned multiple times")
                valid = False
        return valid

    ### Drawing
    def _plot_instance(self, ax):
        x, y = self.instance.location[0]
        ax.scatter(x, y, marker='s', color='blue')
        circle = patches.Circle((x, y), self.instance.radius_chargable, edgecolor='none',
                                facecolor='paleturquoise', linewidth=2, alpha=0.15)
        ax.add_patch(circle)
        x, y = zip(*[self.instance.location[node] for node in self.instance.customer_ids])
        ax.scatter(x, y, marker='x', color='blue')
        x, y = zip(*[self.instance.location[node] for node in self.instance.charger_ids])
        ax.scatter(x, y, marker='P', color='yellow')
        for x, y in zip(x, y):
            circle = patches.Circle((x, y), self.instance.radius_chargable, edgecolor='none',
                                    facecolor='paleturquoise', linewidth=2, alpha=0.15)
            ax.add_patch(circle)
        x, y = zip(*[self.instance.location[node] for node in self.instance.locker_ids])
        ax.scatter(x, y, marker='^', color='red')
        for x, y in zip(x, y):
            circle = patches.Circle((x, y), self.instance.radius_locker, edgecolor='red',
                                    facecolor='none', linewidth=2)
            ax.add_patch(circle)
        
    def _plot_route(self, ax, route: int):
        for trip in self.routes[route]:
            location = [self.instance.location[ID] for ID in trip]
            x, y = zip(*location)
            ax.plot(x, y)

    def _plot_locker(self, ax, locker: ID):
        lx, ly = self.instance.location[locker]
        for customer in self.lockers[locker]:
            cx, cy = self.instance.location[customer]
            ax.plot([cx, lx], [cy, ly], linestyle="dashed", color="grey")

    def _plot_empty(self, ax):
        "Remove all the noise"
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

    ### Easy access
    def _distance(self, node1: ID, node2: ID)->float:
        return float(self.instance.distance.loc[node1, node2])

    def _travel_time(self, node1: ID, node2: ID)->float:
        return float(self.instance.travel_time.loc[node1, node2])

    def _charge_required(self, node1: ID, node2: ID)->float:
        return float(self.instance.charge_required.loc[node1, node2])

    def _demand(self, node: ID) -> int:
        if node in self.instance.customer_ids:
            return self.instance.demand[node]
        if node in self.lockers:
            demand = 0
            for customer in self.lockers[node]:
                demand += self.instance.demand[customer]
            return demand
        return 0

    def _service_time(self, node: ID) -> float:
        if node in self.instance.service_time:
            return self.instance.service_time[node]
        return 0.0
    
    ### Dunder methods
    
    # Dunder method for string (get printed). Not annotaded .sol format.
    def __str__(self):
        # ID name and feasibility
        string = str(self.instance.instance_id) + '\n' + self.name + '\n'
        string += str(self.feasible()) + '\n'
        # Different kinds of cost
        string += f'{self.cost_total():.2f}\n'
        string += f'{self._cost_deployment():.2f}\n'
        string += f'{self._cost_lockers():.2f}\n'
        string += f'{self._cost_distance():.2f}\n'
        string += f'{self._cost_penalty_customers():.4f}\n'
        string += f'{self._cost_penalty_depot():.4f}\n'
        
        # Locker assignment
        string += ','.join(
            '0' if self.assignments[customer] is None else str(self.assignments[customer].locker)
            for customer in range(1, self.instance.num_customers + 1) # ensure order
        )
        string += '\n'
        # Vehicle routes / info
        for route in self._v:
            vid = str(route + 1)
            str_route = [str(node) for trip in self.routes[route] for node in trip]
            string += vid + ',' + ','.join(str_route) + '\n'
            str_charge = [f"{charge:.2f}" for trip in self.charge_quantities[route] for charge in trip]
            string += vid + ',' + ','.join(str_charge) + '\n'
            str_time = [f"{time:.2f}" for trip in self.departure_times[route] for time in trip]
            string += vid + ',' + ','.join(str_time) + '\n'
            
        return string

    def __deepcopy__(self, memo):
        """Create a deepcopy of the Solution object, while keeping instance as a reference"""
        new_copy = Solution(self.instance, self.name)  # Keep instance as reference
        memo[id(self)] = new_copy  # Prevent infinite recursion in case of circular references

        # Deepcopy mutable attributes
        new_copy.routes = copy.deepcopy(self.routes, memo)
        new_copy.loads = copy.deepcopy(self.loads, memo)
        new_copy.assignments = copy.deepcopy(self.assignments, memo)
        new_copy.lockers = copy.deepcopy(self.lockers, memo)
        new_copy.distances = copy.deepcopy(self.distances, memo)
        new_copy.departure_times = copy.deepcopy(self.departure_times, memo)
        new_copy.charge_quantities = copy.deepcopy(self.charge_quantities, memo)

        # Deepcopy boolean flags (not necessary, but for completeness)
        new_copy._changed_distances = self._changed_distances[:]  
        new_copy._changed_departure_times = self._changed_departure_times[:]  
        new_copy._changed_charge_quantities = self._changed_charge_quantities[:]

        return new_copy

    def __repr__(self):
        "The string that represents the object"
        return f"Solution(id={self.instance.instance_id}, name={self.name})"
