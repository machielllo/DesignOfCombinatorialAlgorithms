#ifndef alns_h_oaihf43qasadf
#define alns_h_oaihf43qasadf

#include "../instance.h"
#include "../solution.h"
#include <vector>
#include <random>
#include <functional>

class ALNS {
  const Instance& instance;
  Solution currentSolution;
  Solution bestSolution;
  double temperature;
  std::vector<double> destroyWeights;
  std::vector<double> repairWeights;
  std::vector<std::function<void()>> destroyOperators;
  std::vector<std::function<void()>> repairOperators;
  
  std::mt19937 gen;
  
  void destroy();
  void repair();

  void accessNew(const Solution& newSolution);

  int selectDestroy();
  int selectRepair();

  
  
 public:
  ALNS(const Instance& instance);
  Solution solve(max_iter, max_time, initial_temperature);
  void addRepair(const std::function<void()>& op, double weight);
  void addDestroy(const std::function<void()>& op, double weight);
  
}


#endif 
