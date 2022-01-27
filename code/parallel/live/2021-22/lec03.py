import numpy
from mpi4py import MPI

# pingpong measures message latency.
# Send message from A -> B -> A, measure the time

comm = MPI.COMM_WORLD

def pingpong():
    """
    Send an empty python object from rank 0 to rank 1 and back.

    This uses the pickle protocol, so is quite slow.
    """
    start = MPI.Wtime()
    if comm.rank == 0:
        obj = object()
        comm.send(obj, dest=1)
        obj = comm.recv(source=1)
    elif comm.rank == 1:
        obj = comm.recv(source=0)
        comm.send(obj, dest=0)
    else:
        pass
    return MPI.Wtime() - start


def pingpong_numpy():
    """
    Send an empty numpy array from rank 0 to rank 1 and back.

    This uses the array buffer interface, so is pretty close to the
    speed of C.
    """
    buf = numpy.zeros(1, dtype=int)
    start = MPI.Wtime()
    if comm.rank == 0:
        comm.Send(buf, dest=1)
        comm.Recv(buf, source=1)
    elif comm.rank == 1:
        comm.Recv(buf, source=0)
        comm.Send(buf, dest=0)
    else:
        pass
    return MPI.Wtime() - start


# Some basic warmup timing
time10 = sum(pingpong() for _ in range(10))

nits = int(5 / (time10/10))

# Agree on an iteration count.
nits = comm.allreduce(nits, op=MPI.MIN)

timelots = sum(pingpong_numpy() for _ in range(nits))

print(comm.rank, timelots / nits, flush=True)

# For the nice version of this see pingpong.py
