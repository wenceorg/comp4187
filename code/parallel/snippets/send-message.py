import numpy
from mpi4py import MPI

comm = MPI.COMM_WORLD

rank = comm.rank
size = comm.size

value = numpy.empty(1, dtype=numpy.float64)

if rank == 0:
    value[:] = 10

if rank == 0:
    comm.Ssend([value, 1, MPI.DOUBLE], 1, tag=0)
elif rank == 1:
    print(f"[{rank}]: before receiving, my value is {value}", flush=True)
    comm.Recv([value, 1, MPI.DOUBLE], 0, tag=0)

print(f"[{rank}]: my value is {value}", flush=True)
