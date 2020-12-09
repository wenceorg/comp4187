from mpi4py import MPI  # This automatically calls MPI_Init

comm = MPI.COMM_WORLD

rank = comm.rank
size = comm.size

name = MPI.Get_processor_name()

print(f"Hello, World! I am rank {rank} of {size}. Running on node {name}")

# MPI_Finalize is called in an atexit handler.
