# This automatically calls MPI_Init for us,
# MPI_Finalize is registered in an atexit handler.
from mpi4py import MPI

# Model: have some number of parallel _processes_
# They don't share any memory

# All parallelism comes from communication and synchronisation of the
# processes working collectively on some problem.

# Communication happens through communicators

# This one contains all processes that are running
comm = MPI.COMM_WORLD

# Can ask the communicator, for my identifier within it "rank"
# Can ask the communicator, for its size (the number of processes)

# None of these calls are "collective", they don't synchronise the
# processes at all.
rank = comm.rank

size = comm.size

if False:
    # These prints are unsynchronised, so can appear in any order.
    print(f"Hello, world!, I am {rank} of {size} processes")

# Here we demonstrate how to do synchronous printing.
# The idea is that one process starts a chain of prints and passes a
# token to the next process. Finally the chain ends when we're at the
# end of the chain of processes.

# This magic symbol indicates a source (or destination) process for a
# message that is "empty". A call to receive a message with source
# MPI.PROC_NULL will always return immediately, similary a send to
# MPI.PROC_NULL will return immediately.
devnull = MPI.PROC_NULL

# Synchronisation order
# "Boundary conditions" rank 0 doesn't receive, rank size - 1 doesn't
# send
source = rank - 1 if rank else devnull
dest = rank + 1 if rank != size - 1 else devnull

# All functions are call MPI_Xxx_yyy_zzz
# That's translated into method calls on a communicator
# with name comm.xxx_yyy_zzz
# MPI_Recv receives a message from some source
token = comm.recv(source=source)
print(f"Hello, world!, I am {rank} of {size} processes")
comm.send(token, dest=dest)


# We could wrap this up in a function if we like:

def sync_print(message, comm=MPI.COMM_WORLD):
    """Synchronously print a message in rank order on a communicator.

    comm: The communicator (defaults to COMM_WORLD)"""
    rank = comm.rank
    size = comm.size
    source = rank - 1 if rank else devnull
    dest = rank + 1 if rank != size - 1 else devnull
    token = comm.recv(source=source)
    # The flush is needed because different processes have different
    # stdout buffers
    print(message, flush=True)
    comm.send(token, dest=dest)
    

# Now printing is collective
sync_print(f"Hello, World! {rank}", comm=comm)
