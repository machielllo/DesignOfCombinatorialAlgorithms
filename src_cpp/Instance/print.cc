#include "instance.ih"

void Instance::print() const {
  cout << inst_id << "// Instance id\n";
  cout << "// Description/name of the instance\n";
  cout << num_customers << "// #Customers (int >= 0)\n";
  cout << num_chargers << "// #Chargers (int >= 0)\n";
  cout << num_lockers << "// #Lockers (int >= 0)\n";
  cout << num_vehicles << "// Vehicles (int > 0)\n";
  cout << speed << "// Speed distance per time unit (real > 0)\n";
  cout << vehicle_capacity << "// Max vehicle volume (int > 0)\n";
  cout << battery_capacity << "// Max battery capacity (int > 0)\n";
  cout << discharge_rate << "// Discharge rate per distance unit (real >= 0)\n";
  cout << recharge_rate << "// Recharge rate per time unit (real > 0)\n";
  cout << locker_radius << "// Locker radius (real >= 0)\n";
  cout << cost_locker << "// Locker opening cost (real)\n";
  cout << cost_vehicle << "// Vehicle deployment cost (real)\n";
  cout << cost_distance << "// Cost per time unit late at customer (real)\n";
  cout << cost_customer << "// Cost per time unit late at customer (real)\n";
  cout << cost_depot << "// Cost per time unit late at depot (real)\n";
  for (size_t i = 0; i != num_vehicles; i++) {
    cout << initial_charge[i] << "  ";
  }
  cout << "\n";
  for (size_t i = 0; i != num_nodes; i++) {
    cout << service_time[i] << "  ";
  }
  cout << "\n";
  for (size_t i = 0; i != num_customers + 1; i++) {
    cout << deadline[i] << "  ";
  }
  cout << "\n";
  for (size_t i = 0; i != num_customers + 1; i++) {
    cout << demand[i] << "  ";
  }
  cout << std::endl;
}
