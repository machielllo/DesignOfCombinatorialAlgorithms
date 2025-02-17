#include "alns.ih"

void ALNS::addRepair(const std::function<void()>& op, double weight) {
  repairOperators.push_back(op);
  repairOperators.push_back(weight);
}
