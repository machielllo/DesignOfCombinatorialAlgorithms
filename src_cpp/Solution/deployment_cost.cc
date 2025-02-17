#include "solution.ih"

double Solution::deployment_cost() {
  size_t used_vehicles = 0;
  for (size_t i = 0; i != inst->num_vehicles; i++) {
    if (route[i].size() == 2)
      used_vehicles++;
  }
  return used_vehicles * inst->cost_vehicle;
}
