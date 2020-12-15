import argparse

import numpy
from mpi4py import MPI

parser = argparse.ArgumentParser()
parser.add_argument("n", type=int, help="Size of message to send")

comm = MPI.COMM_WORLD

rank = comm.rank
size = comm.size

args, _ = parser.parse_known_args()

n = args.n
if n <= 0:
    raise ValueError("Size of message must be positive")

send = numpy.full(n, rank, dtype=numpy.int32)
recv = numpy.empty_like(send)

numpy.set_printoptions(threshold=20)
print(f"[{rank}]: about to send {send}", flush=True)
if rank == 0:
    comm.Send([send, n, MPI.INT], 1, tag=0)
    comm.Recv([recv, n, MPI.INT], 1, tag=0)
elif rank == 1:
    comm.Send([send, n, MPI.INT], 0, tag=0)
    comm.Recv([recv, n, MPI.INT], 0, tag=0)
print(f"[{rank}]: received message {recv}", flush=True)
