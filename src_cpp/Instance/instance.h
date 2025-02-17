#ifndef instance_hh_hkadfp0u34q23a
#define instance_hh_hkadfp0u34q23a

#include <string>

struct Location {
  double x;
  double y;

  Location(double x_coord = 0, double y_coord = 0) : x(x_coord), y(y_coord) {}
};


class Instance {
public:
  int inst_id;
  size_t num_customers;
  size_t num_chargers;
  size_t num_lockers;
  size_t num_vehicles;
  size_t num_nodes;
  double speed;
  uint vehicle_capacity;
  double battery_capacity;
  double discharge_rate;
  double recharge_rate;
  double locker_radius;
  double cost_locker;
  double cost_vehicle;
  double cost_distance;
  double cost_customer;
  double cost_depot;
  double* initial_charge;
  double* service_time;
  double* deadline;
  uint* demand;
  Location* location;
  double** distance;

  Instance(const std::string& file_path);
  ~Instance();

  void print_distance() const;
  void print() const;
private:
  void calculate_distance();
};

#endif
