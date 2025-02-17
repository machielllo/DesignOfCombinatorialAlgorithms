#include "instance.ih"

Instance::Instance(const std::string& filename)
  :
  inst_id(0),
  num_customers(0),
  num_chargers(0),
  num_lockers(0),
  num_vehicles(0),
  num_nodes(0),
  speed(0),
  vehicle_capacity(0),
  battery_capacity(0),
  discharge_rate(0),
  recharge_rate(0),
  locker_radius(0),
  cost_locker(0),
  cost_vehicle(0),
  cost_distance(0),
  cost_customer(0),
  cost_depot(0),
  initial_charge(nullptr),
  service_time(nullptr),
  deadline(nullptr),
  distance(nullptr)
{
  ifstream file(filename);
  if (file.is_open()) {
    file >> inst_id >> num_customers >> num_chargers >> num_lockers
	 >> num_vehicles >> speed >> vehicle_capacity >> battery_capacity
	 >> discharge_rate >> recharge_rate >> locker_radius >> cost_locker
	 >> cost_vehicle >> cost_distance >> cost_customer >> cost_depot;

    num_nodes = 1 + num_customers + num_chargers + num_lockers;
    initial_charge = new double[num_vehicles];
    location = new Location[num_nodes];
    service_time = new double[num_nodes];
    deadline = new double[1 + num_customers];
    demand = new uint[1 + num_customers];
    char comma;
    for (size_t idx = 0; idx != num_vehicles; ++idx) {
      uint id;
      double sb;
      file >> id >> comma >> sb;
      initial_charge[idx] = sb;
    }
    size_t id;
    double x, y, st, dl, d;
    file >> id >> comma >> x >> comma >> y >> comma >> dl;	// depot
    location[id] = Location(x, y);
    service_time[id] = 0;
    deadline[id] = dl;
    demand[id] = 0;
    for (size_t idx = 0; idx != num_customers; idx++) {
      file >> id >> comma >> x >> comma >> y >> comma >> st >> comma >> dl >> comma >> d;
      location[id] = Location(x, y);
      service_time[id] = st;
      deadline[id] = dl;
      demand[id] = d;
    }
    for (size_t idx = 0; idx != num_chargers; idx++) {
      file >> id >> comma >> x >> comma >> y;
      location[id] = Location(x, y);
      service_time[id] = 0;
    }
    for (size_t idx = 0; idx != num_lockers; idx++) {
      file >> id >> comma >> x >> comma >> y >> comma >> st;
      location[id] = Location(x, y);
      service_time[id] = st;
    }
    calculate_distance();
  } else {
    std::cerr << "Unable to open file \n";
  }
};

  
Instance::~Instance()
{
  delete[] initial_charge;
  delete[] service_time;
  delete[] deadline;
  delete[] demand;
  delete[] location;

  for (size_t idx = 0; idx != num_nodes; idx++) {
    delete[] distance[idx];
  }

  delete[] distance;
}
