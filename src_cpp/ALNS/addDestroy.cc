#include "alns.ih"

void ALNS::addDestroy(const std::function<void()>& op, double weight) {
  destroyOperators.push_back(op);
  destroyOperators.push_back(weight);
}
