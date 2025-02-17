
# Too much??

# class Destination:
#     def __init__(self, ID):
#         self.ID = ID

# class Customer(Destination):
#     def __init__(self, ID):
#         super().__init__(ID)
#     def __repr__(self):
#         return f'C{self.ID}'

# class Station(Destination):
#     def __init__(self, ID, charge_time):
#         super().__init__(ID)
#         self.charge_time = charge_time
        
#     def __repr__(self):
#         return f'S{self.ID}, {self.charge_time:.2f}'

# class Locker(Destination):
#     def __init__(self, ID):
#         super().__init__(ID)
        
#     def __repr__(self):
#         return f'L{self.ID}'

# class Depot(Destination):
#     def __init__(self):
#         self.ID = 0
#         self.location = (0, 0)
#     def __repr__(self):
#         return '0'