#include "solution.ih"

double Solution::objective_value() {
  double val = 0;
  val += distance_cost();
  val += penalty_customers();
  val += penalty_depot();
  val += deployment_cost();
  val += locker_cost();
  return val;
}
