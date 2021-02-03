# We're going to write code that runs a pingpong between two processes
# (and leaves remaining ones idle). The goal being to get data from
# which we can fit the message latency and inverse bandwidth for the
# model of time for sending messages we had in the lectures
#
# t(m) = α + β m
#
# With α the message latency and β the inverse bandwidth, m the size
# of a message in bytes.

import argparse
import sys

import numpy
from mpi4py import MPI

parser = argparse.ArgumentParser()
parser.add_argument("output_file", type=str,
                    help="Write data to specified numpy file"
                    " (load with numpy.load)")
parser.add_argument("--use-pickle", action="store_true",
                    default=False,
                    help="Send messages using pickle interface? "
                    "If False (default), send numpy buffers")
args, _ = parser.parse_known_args()
if MPI.COMM_WORLD.size < 2:
    print("Need at least two processes")
    sys.exit(1)


def pingpong(m, comm=MPI.COMM_WORLD, use_numpy=True):
    buf = numpy.empty(m, dtype=numpy.int8)
    size = buf.nbytes
    if comm.rank == 0:
        print(f"Running pingpong: {size} bytes; use_numpy {use_numpy}",
              flush=True)

    def backandforth(nits):
        # Need this so that the assignment to buf below writes to the
        # lexically closed over variable defined above.
        nonlocal buf
        for _ in range(nits):
            if comm.rank == 0:
                if use_numpy:
                    comm.Send(buf, dest=1, tag=0)
                    comm.Recv(buf, source=1, tag=0)
                else:
                    comm.send(buf, dest=1, tag=0)
                    buf = comm.recv(source=1, tag=0)
            elif comm.rank == 1:
                if use_numpy:
                    comm.Recv(buf, source=0, tag=0)
                    comm.Send(buf, dest=0, tag=0)
                else:
                    buf = comm.recv(source=0, tag=0)
                    comm.send(buf, dest=0, tag=0)
            else:
                pass
    # Try and figure out how many iterations to run for.
    nwarmup = 1
    total = 0
    while total < 0.1:
        start = MPI.Wtime()
        backandforth(nwarmup)
        total = MPI.Wtime() - start
        nwarmup *= 2

    # Everyone has their own value of total
    # Combine across the communicator, picking the maximum value
    maxtotal = comm.allreduce(total, op=MPI.MAX)
    # Also need to combine warmups, use minimum value here
    minwarmup = comm.allreduce(nwarmup, op=MPI.MIN)

    # This will be the same on all processes
    single_iteration_time = maxtotal / minwarmup

    # Pick a number of iterations that will maybe run for 2 seconds.
    nits = max(1, int(2 / single_iteration_time))

    start = MPI.Wtime()
    backandforth(nits)
    total = MPI.Wtime() - start
    single_iteration_time = comm.allreduce(total, op=MPI.MAX) / nits
    return size, single_iteration_time


# Messages between 1 and 2**27 bytes in size.
sizes = numpy.unique(numpy.logspace(0, 27, num=56, base=2, dtype=numpy.int32))
if args.use_pickle:
    # Avoid very large messages with pickle
    sizes = sizes[:-3]

data = numpy.asarray([pingpong(m, use_numpy=not args.use_pickle)
                      for m in sizes])

if MPI.COMM_WORLD.rank == 0:
    numpy.save(args.output_file, data)
