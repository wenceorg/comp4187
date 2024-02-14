from mpi4py import MPI

world_rank = MPI.COMM_WORLD.rank
world_size = MPI.COMM_WORLD.size

self_rank = MPI.COMM_SELF.rank
self_size = MPI.COMM_SELF.size

print(f"Hello, I am process {world_rank} of {world_size} in COMM_WORLD;"
      "in COMM_SELF I am process {self_rank} of {self_size}", flush=True)
