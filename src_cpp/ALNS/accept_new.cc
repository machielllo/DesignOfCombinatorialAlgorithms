#include "alsn.ih"

void ALNS::accessNew(const Solution& newSolution) {
  if (newSolution.objectiveValue - bestSolution.objectiveValue > 0) {
    bestSolution = newSolution;
    currentSolution = newSolution;
    return
  }
  double diffCurrent = newSolution.objectiveVlaue - currentSolution.objectiveValue;
  if (diffCurrent > 0)
    currentSolution = newSolution;
  else {
    double annealingValue = exp(diffCurrent / temperature);
    if (getRandomBoolean(annealingValue))
      currentSolution = newSolution;
  }
}
