#include "solution.ih"

double Solution::total_distance() {
  double val = 0;
  uint prev, next;
  for (size_t i = 0; i != inst.num_vehicles; i++) {
    prev = 0;
    for  (size_t j = 0; i < route[j].size(); j++) {
      next = route[i][j];
      val += inst->distance[prev, next];
    }
  }
  return val;
}
