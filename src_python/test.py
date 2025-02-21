from instance import Instance
from solution import Solution, Index
from copy import copy

instance = Instance('../Toys/Not Annotated/996.inst')
self = Solution(instance, name="Empty 996")

print(self)

self.insert(Index(0, 0, 1, 0), 1)
self.insert(Index(0, 0, 1, 0), 2)
self.insert(Index(1, 0, 1, 0), 3)
self.insert(Index(2, 0, 1, 0), 4)

print(self)



# # print(self)

# index = Index(0, 0, 1, 0)
# node = 1
# # self.insert(Index(0, 0, 1, 0), 1)
# print(self)

self.write('test.sol')

print(self)

self.insert_cost(Index(0, 0, 1, 0), 1)
self.insert_cost(Index(1, 0, 1, 0), 1)
self.insert_cost(Index(2, 0, 1, 0), 1)
self.insert_cost(Index(3, 0, 1, 0), 1)

# self.insert(Index(3, 0, 1, 0), 1)


# index = Index(0, 0, 1, 0)

# def change_index(index: Index) -> Index:
#     index.locker += 1
#     return index

# index_copy = change_index(index)

# index is index_copy

# index_copy = index.copy()


# index_copy.locker = 1

# index


