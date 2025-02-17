#include "instance.ih"

void Instance::calculate_distance() {
  distance = new double*[num_nodes];
  for (size_t idx = 0; idx != num_nodes; idx++) {
    distance[idx] = new double[num_nodes];
  }
  for (size_t i = 0; i != num_nodes; ++i) {
    for (size_t j = 0; j != num_nodes; ++j) {
      double dx = location[i].x - location[j].x;
      double dy = location[i].y - location[j].y;
      distance[i][j] = sqrt(dx * dx + dy * dy);
    }
  }
}
