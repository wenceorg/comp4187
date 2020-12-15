---
title: "Collectives"
weight: 3
katex: true
---

# Collective communication

[Point-to-point]({{< ref "point-to-point.md" >}}) messages are
sufficient to write all the parallel algorithms we might want.
However, they might not necessarily be the most efficient.

As motivation, let's think about the time we would expect the [ring
reduction]({{ ref "mpi-ring.md" }}) you implemented to take as a
function of the number of processes.

Recall from the [ping-pong exercise]({{ ref "mpi-ping-pong.md" }})
that our model for the length of time it takes to send a message with
$B$ bytes is

$$
T(B) = \alpha + \beta B
$$

To rotate each item all the way around a ring of $P$ processes
requires each process to send $P-1$ messages. Again supposing we
reduce $B$ bytes:

$$
T_\text{ring}(B) = (P-1)(\alpha + \beta B)
$$

So as we add more processes, the time scales linearly.

An alternative is to combine the partial reductions pairwise in a
tree, as shown in the figure below

{{< manfig
    src="mpi-tree-reduce.svg"
    width="75%"
    caption="Tree reduction across 16 processes. At each level processes combine pairwise." >}}

This approach can be generalised to problems where the number of
processes is not a power of two.

To get the result back to all processes, we can just send the combined
final value back up the tree in the same manner. For $P$ processes,
the tree has depth $\log_2 P$ (we divide the number of by two each
time). So now we only send $2 \log_2 P$ messages (up and down), for a
total time of

$$
T_{\text{tree}}(B) = 2\log_2 P (\alpha + \beta B)
$$

As long as $2\log_2 P < (P-1)$ this takes less overall time. We can
solve this numerically to find it should be preferable as long as $P >
6$.

```python
import numpy
import scipy.optimize


# Do Newton to find P such that 2log_2 P - (P-1) = 0
# We know that P = 1 is a solution, so we deflate that away
def f(p):
    return 1/abs(p-1) * (2*numpy.log2(p) - (p - 1))


root = scipy.optimize.newton(f, 2)

print(root)
=> 6.319722355838366
```

{{< autofig
    src="log-tree-minimum-p.svg"
    width="50%"
    caption="Modelled time to compute a reduction using a 1D ring and a tree, as soon as $P > 6$, the tree is faster"  >}}


We conclude that some kind of tree-based reduction is superior in
almost all circumstances.

This reduction is an example of a _collective_ operation. Rather than
sending messages pairwise, all processes in a communicator
work together (or collectively) to compute some result.

## What about implementation?

Writing code for a tree-reduction in MPI by hand is actually not too
hard, and you can have a go if you want.

However, writing it generically to handle all datatypes is slightly
fiddly, and moreover, depending on the topology of the underlying
network, other approaches might be more efficient. For example,
[hypercubes](https://en.wikipedia.org/wiki/Hypercube_(communication_pattern))
often offer a superior communication pattern.

Our conclusion then, is that we probably don't want to implement this
stuff ourselves.

Fortunately, MPI offers a broad range of builtin collective
operations that cover most of the communication patterns we might want
to use in a parallel program. It now falls to the implementor of the
MPI library (i.e. not us) to come up with an efficient implementation.

{{< hint info >}}

This is perhaps a general pattern that we observe when writing MPI
programs. It is best to see if our communication pattern fits with
something the MPI library implements before rolling our own.

{{< /hint >}}

## Types of collectives

One thing to note with all of these collectives is that none of them
require a _tag_. MPI therefore just matches collectives in the order
that they are called. So we need to be careful that we call
collectives in the same order on all processes.

{{< hint info >}}

All of the collective operations we introduce in this section are
blocking: they only return once all processes in the communicator have
called them, at which point the input and output buffers are safe to
reuse.

MPI-3 (standardised in around 2014) introduce _non-blocking_ versions
of all the collectives (with names starting with `MPI_I` like the
non-blocking point-to-point functions). These have the same semantics,
but we get an `MPI_Request` object that we must wait on before we can
look at the results.

The rationale for the introduction of non-blocking collectives was
similar to that for non-blocking point-to-point: they allow some
overlap of communication latency with computation, potentially
enabling more scalable code.

{{< /hint >}}

### Barrier: `MPI_Barrier`

We already saw a barrier in OpenMP, MPI similarly has one, named
[`MPI_Barrier`](https://rookiehpc.com/mpi/docs/mpi_barrier.php).

```py
comm.Barrier()
```

In a barrier, no process may exit the barrier until all have entered.
So we can use this to provide a synchronisation point in a program.
Note that there are no guarantees that all processes leave at the same
time.

{{< hint warning >}}

There are actually very few reasons that a correct MPI code needs a
barrier.

The usual reason to add them is if we want to measure the parallel
performance of some part of the code, and don't want bad load balance
from another part to pollute our measurements.

{{< /hint >}}

### Reductions

These _are_ useful, there are few related ones.

[`MPI_Reduce`](https://rookiehpc.com/mpi/docs/mpi_reduce.php) combines
messages with a provided operation and accumulates the final result on
a specified `root` rank.

```py
comm.Reduce([sendbuf, count, datatype],
            [recvbuf, count, datatype],
            op, root)
```

Every process provides a value in `sendbuf`, the root process (often
rank 0, but not necessarily) provides an output buffer in `recvbuf`.
The count and datatype arguments are the same as for point-to-point
messaging, they describe how the send and receive buffers are to be
interpreted by MPI. The `op` argument tells MPI how to combine values
from different processes.

{{< manfig
    src="mpi-reduce.svg"
    width="50%"
    caption="`MPI_Reduce` combines values with a specified operation and places the result on the `root` process." >}}

Closely related is
[`MPI_Allreduce`](https://rookiehpc.com/mpi/docs/mpi_allreduce.php)
which does the same thing as `MPI_Reduce` but puts the final result on
all processes (so there is no need for a `root` argument.

```py
comm.Allreduce([sendbuf, count, datatype],
               [recvbuf, count, datatype],
               op)
```

{{< hint info >}}
We can use the magic value `MPI.IN_PLACE` in place of the
specification of the send buffer to state that the initial value in
the receive buffer should be sent.

```py
recvbuf[:] = stuff_to_send
comm.Allreduce(MPI.IN_PLACE, [recvbuf, count, datatype], op)
# Is equivalent to
comm.Allreduce([stuff_to_send, count, datatype],
               [recvbuf, count, datatype], op)
```

{{< /hint >}}

{{< manfig
    src="mpi-allreduce.svg"
    width="50%"
    caption="`MPI_Allreduce` combines values with a specified operation and places the result on all processes." >}}

`MPI_Allreduce` is generally more useful than `MPI_Reduce`, since
often we need to make a collective decision based on the result of the
reduction (for example when checking for convergence of a numerical
algorithm). Although it is possible to implement an allreduce using an
`MPI_Reduce` followed by an
[`MPI_Bcast`](https://rookiehpc.com/mpi/docs/mpi_bcast.php), more
efficient algorithms exist.

There are also "prefix reduction" versions,
[`MPI_Scan`](https://rookiehpc.com/mpi/docs/mpi_scan.php) and
[`MPI_Exscan`](https://rookiehpc.com/mpi/docs/mpi_exscan.php) (for
inclusive and exclusive "scans" of the input respectively).

```py
comm.Scan([sendbuf, count, datatype],
          [recvbuf, count, datatype],
          op)
comm.Exscan([sendbuf, count, datatype],
            [recvbuf, count, datatype],
            op)
```

{{< columns >}}

{{< manfig
    src="mpi-scan.svg"
    width="100%"
    caption="`MPI_Scan` computes an inclusive prefix reduction." >}}

<--->

{{< manfig
    src="mpi-exscan.svg"
    width="100%"
    caption="`MPI_Exscan` computes an exclusive prefix reduction, on rank 0 the value in the output buffer is undefined." >}}

{{< /columns >}}

The final missing piece is what this magic `op` argument is. For
combining simple types, we usually can use one of a number of builtin
options given to us by MPI.

| Description    | Operator                                                  | Identity element                   |
|----------------|-----------------------------------------------------------|------------------------------------|
| Addition       | [`MPI.SUM`](https://rookiehpc.com/mpi/docs/mpi_sum.php)   | 0                                  |
| Multiplication | [`MPI.PROD`](https://rookiehpc.com/mpi/docs/mpi_prod.php) | 1                                  |
| Minimum        | [`MPI.MIN`](https://rookiehpc.com/mpi/docs/mpi_min.php)   | Most positive number of given type |
| Maximum        | [`MPI.MAX`](https://rookiehpc.com/mpi/docs/mpi_max.php)   | Most negative number of given type |
| Logical and    | [`MPI.LAND`](https://rookiehpc.com/mpi/docs/mpi_land.php) | True                               |
| Logical or     | [`MPI.LOR`](https://rookiehpc.com/mpi/docs/mpi_lor.php)   | False                              |
| Logical xor    | [`MPI.LXOR`](https://rookiehpc.com/mpi/docs/mpi_lxor.php) | False                              |
| Bitwise and    | [`MPI.BAND`](https://rookiehpc.com/mpi/docs/mpi_band.php) | All bits 1                         |
| Bitwise or     | [`MPI.BOR`](https://rookiehpc.com/mpi/docs/mpi_bor.php)   | All bits 0                         |
| Bitwise xor    | [`MPI.BXOR`](https://rookiehpc.com/mpi/docs/mpi_bxor.php) | All bits 0                         |


If we pass a `count` of more than 1, then the operation is applied to
each entry in turn. So

```py
send = numpy.empty(2, dtype=numpy.int32)
recv = numpy.empty(2, dtype=numpy.int32)
send[:] = ...
comm.Allreduce([send, 2, MPI.INT32_t],
               [recv, 2, MPI.INT32_t], op=MPI.SUM)
```

Produces the sum over all processes of `send[0]` in `recv[0]` and that
of `send[1]` in `recv[1]`.

When computing a minimum or maximum value, we might also want to know
on which process the value was found. This can be done using the
combining operations
[`MPI.MINLOC`](https://www.mpi-forum.org/docs/mpi-3.1/mpi31-report/node114.htm#Node114) and
[`MPI.MAXLOC`](https://www.mpi-forum.org/docs/mpi-3.1/mpi31-report/node114.htm#Node114). These
also show an example of using more complicated datatypes.

Suppose we have a pair of values

```c
struct ValAndLoc {
  double x;
  int loc;
};
```

We put the value we care about in the first slot, and the rank of the
current process (say) in the second. Now combining with `MPI_MAXLOC`
produces the `MAX` over the first slot, and just copies the second
slot over.

```py
# This is how you make a structured datatype in numpy
dtype = numpy.dtype([('x', numpy.float64), ('loc', numpy.int32)])
local = numpy.empty(1, dtype=dtype)
local[0]["x"] = ...;
local[0]["loc"] = rank;

global_ = numpy.empty_like(dtype)
comm.Allreduce([local, 1, MPI.DOUBLE_INT],
               [global_, 1, MPI.DOUBLE_INT],
               MPI.MAXLOC)
```

So we can determine the maximum value, and also the rank on which it
was found.

### One to all: scatters and broadcasts

When starting up a simulation, we might want to read some
configuration file to provide parameters. This typically should only
be done by a single process[^1], however, all processes will need to
know the values so that they can configure the simulation
appropriately.

To do this we can broadcast data from a single rank using
[`MPI_Bcast`](https://rookiehpc.com/mpi/docs/mpi_bcast.php).

```py
comm.Bcast([buffer, count, datatype], root)
```

{{< manfig
    src="mpi-bcast.svg"
    width="50%"
    caption="`MPI_Bcast` sends data from a root rank to all ranks in the communicator." >}}

Note that the value in the buffer for input purposes only matters on
the root process, but all processes must provide enough space. For
example, to send 10 integers from rank 0

```py
buffer = numpy.empty(10, dtype=numpy.int32)
if comm.rank == 0:
   # Initialise values from somewhere (e.g. read from file)
   ...
comm.Bcast([buffer, 10, MPI.INT32_T], 0, comm);
```

A more general broadcast mechanism, where each rank receives different
data, is provided by
[`MPI_Scatter`](https://rookiehpc.com/mpi/docs/mpi_scatter.php), which
takes some data on a single rank, and splits it out to all processes.

```py
comm.Scatter([sendbuf, sendcount, sendtype],
             [recvbuf, recvcount, recvtype],
             root)
```

{{< manfig
    src="mpi-scatter.svg"
    width="50%"
    caption="`MPI_Scatter` splits and sends data on the root rank to all ranks in the communicator." >}}

{{< hint warning >}}
Note that the `sendcount` argument is the number of values to send to
each process (not the total number of values in the send buffer). On
ranks other than the root rank, the send parameters are ignored (so
the `sendbuf` argument can be `None`).
{{< /hint >}}

For example, consider again a situation where rank zero reads a
configuration file and then determines some allocation of work
(perhaps loop iteration counts) for each process. We need to
communicate a pair of "start" and "end" values to each process.

```py
rank = comm.rank
recvbuf = numpy.empty(2, dtype=numpy.int32)

if rank == 0:
    size = comm.size
    sendbuf = numpy.empty(2*size, dtype=numpy.int32)
    # Populate sendbuf somehow
    ...
    # Note how sendbuf is 2*size, but the count is 2, because we send
    # 2 entries to each process
    comm.Scatter([sendbuf, 2, MPI.INT32_T], [recvbuf, 2, MPI.INT32_T],
                 root=0)
else:
    comm.Scatter(None, [recvbuf, 2, MPI.INT32_T], root=0)
```


This sends entries 0 and 1 in sendbuf to rank 0; entries 2 and 3 to
rank 1; entries 4 and 5 to rank 2; and so on.

There is also a more general
[`MPI_Scatterv`](https://rookiehpc.com/mpi/docs/mpi_scatterv.php),
in which we can specify how many values we send to each process.

### All to one: gathers

The dual to
[`MPI_Scatter`](https://rookiehpc.com/mpi/docs/mpi_scatter.php), in
which we gather all values to a single process is (perhaps
unsurprisingly) called
[`MPI_Gather`](https://rookiehpc.com/mpi/docs/mpi_gather.php)

```py
comm.Gather([sendbuf, sendcount, sendtype],
            [recvbuf, recvcount, recvtype],
            root)
```

{{< hint warning >}}

Note again that the `recvcount` argument is the number of entries to
receive _from each process_. The buffer must be big enough to receive
`comm.size*recvcount` total entries.
{{< /hint >}}

{{< manfig
    src="mpi-gather.svg"
    width="50%"
    caption="`MPI_Gather` gathers data from all ranks to a root rank." >}}

We might use this, for example, to collect output data before writing
it to a file[^2].

Just like `MPI_Scatter`, there is a more general
[`MPI_Gatherv`](https://rookiehpc.com/mpi/docs/mpi_gatherv.php) in
which we specify how many values to gather from each process.

[^1]: All processes simultaneously accessing the same file can be very
    slow on some systems.

[^2]: In real-world applications you should use a more scalable,
    parallel, approach. For example, directly using MPI-IO (see [Bill
    Gropp's](https://wgropp.cs.illinois.edu)
    [slides](https://wgropp.cs.illinois.edu/courses/cs598-s15/lectures/lecture32.pdf)
    for a nice intro and motivation), or a higher-level alternative
    like [HDF5](https://www.hdfgroup.org). These additional libraries
    are beyond the scope of this course.

### All to all: everyone talks to everyone

Generally, we would like to avoid parallelisation that requires that
we have data whose size scales with the total number of processes on
every rank, or where every process must communicate with every other,
sometimes this is unavoidable.

For example, multi-dimensional [fast Fourier
transforms](https://en.wikipedia.org/wiki/Fast_Fourier_transform) are
among the fastest approaches for computing the inverse of the
Laplacian in periodic domains. They form, amongst other things, a core
computational component of numerical simulation of turbulent flow (see
for example the codes at https://github.com/spectralDNS).

To compute Fourier transforms in parallel, we need to do
one-dimensional transforms along each cartesian direction,
interspersed by a global transpose of the data. Depending on the data
distribution, this is a generalised "all to all" communication
pattern. See
[mpi4py-fft](https://mpi4py-fft.readthedocs.io/en/latest/introduction.html)
for a high-performance Python library that does this.

MPI provides a number of routines that help with these including

- [`MPI_Allgather`](https://rookiehpc.com/mpi/docs/mpi_allgather.php)
  (and its "vector" sibling
  [`MPI_Allgatherv`](https://rookiehpc.com/mpi/docs/mpi_allgatherv.php)).
- [`MPI_Alltoall`](https://rookiehpc.com/mpi/docs/mpi_alltoall.php)

```py
comm.Allgather([sendbuf, sendcount, sendtype],
               [recvbuf, recvcount, recvtype])
comm.Alltoall([sendbuf, sendcount, sendtype],
               [recvbuf, recvcount, recvtype])
```

Note how neither of these calls has a `root` argument: there is no
"special" process in these collectives.

The pictorial version of the routines is shown below

{{< manfig
    src="mpi-allgather.svg"
    caption="`MPI_Allgather` acts like `MPI_Gather` but no process is special." 
    width="50%">}}

Note how the `MPI_Alltoall` call ends up transposing the data.
{{< manfig
    src="mpi-alltoall.svg"
    width="50%"
    caption="`MPI_Alltoall` sends data from all processes to all processes, transposing along the way." >}}

## Summary

MPI has a rich array of _collective_ operations which can be used to
implement common communication patterns much more efficiently than we
are likely to write by hand using only point-to-point messaging.

Unlike point-to-point messaging, there are no tags in collective
operations, so collectives are matched "in-order" on the communicator
they are used with. We briefly look at how to distinguish collective
operations, and how to restrict the operation to a subset of all the
processes in `MPI_COMM_WORLD` when considering [communicator
manipulation]({{< ref "advanced.md#communicators" >}}).
