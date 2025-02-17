#include "solution.ih"


Solution::Solution(const Instance& inst)
  :
  inst(inst)
  route(nullptr)
  locker_assignment(nullptr)
  load(nullptr)
  recharge(nullptr)
  name("")
  objective_value(0.0)
{
  // Contructive Heuristic
  bool visited[inst.num_customers + 1];
  fill(begin(visited), end(visited), false);
  visited[0] = true;

  route = new vector<uint>[inst.num_vehicles];
  for (size_t idx = 0; idx != inst.num_vehicles; idx++) {
    route[idx] = vector<uint>(2, 0);
  }
  locker_assignment = new uint[inst.num_customers + 1];
  fill(begin(locker_assignment), end(locker_assignment), 0);
  load = new Vec<uint>[inst.num_vehicles];
  recharge = new Vec<float>[inst.num_vehicles];
  
  
  while (all_of(begin(visited), end(visited) { return v; })) {
    
    
  }
	 
		
}
