#include "main.ih"

int main(int argc, char **argv)
try
{
  string inst_path = argv[1];
  // Arguments args = parse_args(argc, argv);
  Instance inst = Instance(inst_path);
  inst.print();
  inst.print_distance();
  // Solution sol = full_solve(inst);
  // sol.write_out(args.sol_path);
}
catch (...)
{
    return 1;
}
