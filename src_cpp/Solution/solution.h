#ifndef solution_hh_o6t8o34gqa
#def solution_hh_o6t8o34gqa

#include <vector>
#include "../Instance/instance.h"
#include <string>

class Solution {

public:
  const Instance& inst;
  std::vector<uint>* route;
  std::vector<uint>* locker_assignment;
  std::vector<uint>* load;
  std::vector<double>* recharge;
  std::string name;
  double objective_value;

  
  Solution(const Instance& int);
  
  bool feasible() const;
  void print() const;
  double objective_value();
  double deployment_cost();
  double distance_cost();
  double total_distance();
  double penalty_customers();
  double penalty_depot();
};
#endif
