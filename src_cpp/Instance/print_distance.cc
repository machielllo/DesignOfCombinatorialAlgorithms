#include "instance.ih"

void Instance::print_distance() const {
  for (uint i = 0; i < num_nodes; ++i) {
    for (uint j = 0; j < num_nodes; ++j) {
      std::cout << distance[i][j] << " ";
    }
    std::cout << std::endl;
  }
}
