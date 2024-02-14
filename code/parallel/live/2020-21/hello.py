from mpi4py import MPI

# A communicator with all parallel processes in it
comm = MPI.COMM_WORLD

# A communicator separate for each process.
comm_self = MPI.COMM_SELF

# Print synchronised
# Relay: rank 0 prints first, then passes a message to rank 1, ...

rank = comm.rank
size = comm.size

if rank == size - 1:
    # A bit-bucket (/dev/null) destination or source.
    # Sends to this destination return immediately.
    dest = MPI.PROC_NULL
else:
    # Otherwise, send to process to my right.
    dest = rank + 1

if rank == 0:
    src = MPI.PROC_NULL
else:
    # Receive from process on my left.
    src = rank - 1

# We're only using the messages for synchronisation, so don't actually
# care about the object we receive
_ = comm.recv(source=src)
print(f"Hello, World! I am {comm.rank} of {comm.size}")
# Lowercase: send python objects (via pickle). Slow, much copies
comm.send(object(), dest=dest)
