#include "solution.ih"

double Solution::distance_cost() {
  return total_distance() * inst->cost_distance;
}
