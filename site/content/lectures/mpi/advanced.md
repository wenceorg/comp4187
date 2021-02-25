---
title: "Advanced topics"
weight: 4
---

# Some pointers to more advanced features of MPI

## Communicator manipulation {#communicators}

We saw that we can distinguish point-to-point messages by providing
different tags, but that there was no such facility for collective
operations. Moreover, a collective operation (by definition) involves
all the processes in a communicator.

This raises two questions:

1. How can we have multiple collective operations without them
   interfering with each other;
2. What if we want a collective operation, but using only a subset of
   the processes (e.g. only processes with an even rank)?

We might worry that we're reduced to writing everything by hand using
point-to-point messages, but fear not, MPI has us covered.

### Duplicating communicators

To address point 1, collective operations match based on the
communicator context, and MPI allows us to
[_duplicate_](https://www.mpich.org/static/docs/v3.3/www3/MPI_Comm_dup.html)
communicators. This provides us with a new communicator that contains
exactly the same set of processes with the same ranks, but collectives
on one communicator won't interfere with those on another (and
similarly for point-to-point messages).

```c
int MPI_Comm_dup(MPI_Comm incomm, MPI_Comm *outcomm);
```

This is a very useful thing to use if you are writing a library that
uses MPI. Whenever someone calls your library you do

```c
MPI_Comm_dup(user_communicator, &library_communicator);
```

and then always use the `library_communicator` inside your library.
Now you can _guarantee_ that you will never accidentally match any
messages or collectives that the user runs on their
`user_communicator`.

When we are done, we should release the communicator we duplicated (so
as not to leak memory) by calling `MPI_Comm_free`

```c
int MPI_Comm_free(MPI_Comm *comm);

/* To release a communicator: */
MPI_Comm_free(&library_communicator);
```

### Splitting communicators into subgroups

This is useful if want some collective operation over a subset of all
the processes, for example we want to gather along the rows of a
distributed matrix. This can be done by calling `MPI_Comm_split`

```c
int MPI_Comm_split(MPI_Comm incomm, int colour, int key, MPI_Comm *newcomm);
```

The `colour` decides which ranks in `incomm` end up in the same
`newcomm`. Ranks that provide the same `colour` will be in the same
group. The `key` can be used to provide an ordering of the ranks in
the new group, usually we pass the rank from the `incomm`.

For example, to create a communicator that splits into the processes
in `MPI_COMM_WORLD` into a even and odd processes we can use.


```c
int rank;
MPI_Comm incomm = MPI_COMM_WORLD;
MPI_Comm newcomm;
MPI_Comm_rank(incomm, &rank)
MPI_Comm_split(incomm, rank % 2, rank, &newcomm);
/* Do stuff with newcomm */
/* Release once we are done */
MPI_Comm_free(&newcomm);
```

Here's a picture:

{{< manfig
    src="comm-world-split.svg"
    width="75%"
    caption="`MPI_Comm_split` can split a communicator into smaller ones which can then proceed independently." >}}
    
We emphasise again that this does not produce new processes, it just
provides a communication context that does not contain all processes.

{{< exercise >}}

[`code/mpi-snippets/split-comm.c`]({{< code-ref
"code/mpi-snippets/split-comm.c" >}}) contains a simple example.
Have a look at the code and compile and run it.

Do you understand the output?

Do you understand why there is only one `splitcomm` variable (despite
splitting the input communicator into two)?

{{< /exercise >}}

This splitting facility is useful if we only need a subset of all the
processes to participate in a collective operation. This might be
something like reducing the number of processes participating in the
[coarse grids of a multigrid solve](https://arxiv.org/abs/1604.07163).

## Further features and details

In addition to what we've seen, MPI provides a number of other
features that are useful for writing libraries. We won't cover them in
detail, but just mention some aspects.

### File IO

MPI, via
[MPI-IO](https://www.mpi-forum.org/docs/mpi-3.1/mpi31-report/node305.htm#Node305),
provides a portable and high-performance way of reading and writing
files in parallel. This forms the backbone of higher-level parallel
file libraries like [HDF5](https://www.hdfgroup.org) and
[NetCDF](https://www.unidata.ucar.edu/software/netcdf/).

### [Profiling interface](https://www.mpi-forum.org/docs/mpi-3.1/mpi31-report/node357.htm#Node357)

All MPI functions (everything called `MPI_XXX`) are actually just
wrappers around internal "profiling" functions whose names start with
`PMPI_XXX`. For example, `MPI_Send` is implemented in the MPI library as

```c
int MPI_Send(const void *sendbuf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
{
  return PMPI_Send(sendbuf, count, datatype, dest, tag, comm);
}
```

The public `MPI_` functions are exported with [weak symbol
binding](https://en.wikipedia.org/wiki/Weak_symbol) so we can override
them. For example, suppose that we want to print a message every time
an `MPI_Send` is called, our code could do:

```c
int MPI_Send(const void *sendbuf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
{
  printf("Sending message to %d\n", dest);
  return PMPI_Send(sendbuf, count, datatype, dest, tag, comm);
}
```

This facility is used to write tools that can produce timelines of
message-passing in a parallel program. These include

- [The MPI Parallel Environment](https://www.mcs.anl.gov/research/projects/perfvis/software/MPE/)
- [Score-P](https://www.vi-hps.org/projects/score-p/)
- [Scalasca](http://www.scalasca.org)
- [Tau](http://www.cs.uoregon.edu/research/tau/home.php)

### One-sided messaging and Remote Memory Access

All of the messaging we saw was _two-sided_, in that we need both a
send and a receive. MPI-2 introduced, and MPI-3 extended and improved,
support for one-sided messages and direct access to remote
(off-process) memory. For details on these features, if you're
interested, I recommend the books [Using
MPI](https://mitpress.mit.edu/books/using-mpi-third-edition) and
[Using Advanced
MPI](https://mitpress.mit.edu/books/using-advanced-mpi). See also
[Torsten Hoefler's
tutorials](https://htor.inf.ethz.ch/teaching/mpi_tutorials/).

## Language bindings and libraries

[Julia](https://julialang.org) has MPI bindings in
[MPI.jl](https://github.com/JuliaParallel/MPI.jl), and
distributed arrays in the
[MPIArrays.jl](https://github.com/barche/MPIArrays.jl) package.

As we've seen in this course, Python has wrappers via
[mpi4py](https://mpi4py.readthedocs.io/en/stable/). For distributed
array computation, look at [dask](https://dask.org).

For parallel sparse linear algebra, and PDE solvers,
[PETSc](https://www.mcs.anl.gov/petsc) and
[Trilinos](https://trilinos.github.io) are robust and well-supported
libraries. PETSc has mature Python bindings provided by [petsc4py]({{<
ref "petsc4py.md" >}}).

