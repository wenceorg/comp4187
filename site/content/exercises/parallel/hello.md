---
title: "Parallel Hello World"
weight: 1
katex: false
---

# Hello, World!

Every programming course has to start with "hello world", this is no
exception. The goal of this is to familiarise you with compiling and
running code using MPI, the parallel library we'll be using, either on
Hamilton, or your own machine. So take a look at the [setup guide]({{<
ref "/setup/mpi.md" >}}) if you haven't already.

## A C version {#mpi}

MPI is a specification for a library-based programming model. The
standard specifies Fortran and C/C++ interfaces, and there are
wrappers for many popular programming languages including
[Python](https://mpi4py.readthedocs.io/en/stable/) and
[Julia](https://github.com/JuliaParallel/MPI.jl).

On Hamilton, we need to load the right modules. We'll need a modern
version of the GCC compiler, along with an MPI library. If you're
running on your own system and have set things up right, you don't
need modules.

To load a module (which sets up the environment) we need to run
`module load MODULENAME`. So log in and load

```
gcc/9.3.0
intelmpi/gcc/2019.6
```

Our hello world code looks like this

{{< code-include "parallel/hello/hello.c" "c" >}}

This doesn't look that different from a serial hello world, except
there are a bunch of additional calls to library functions whose names
start with `MPI_`.

To compile this file, we need to tell the compiler about all the
MPI-relevant include files and libraries to link. Since this is
complicated, MPI library implementors typically ship with _compiler
wrappers_ that set the right flags. On Hamilton these are named
`mpicc` (for the MPI wrapper around the C compiler), `mpicxx` (for the
wrapper around the C++ compiler), and `mpif90` (for the Fortran
wrapper). Since we have a C source file, we should use `mpicc`
```
$ mpicc -o hello hello.c
```

Running the executable is now also more complicated, we need to use
`mpirun` to launch it. This takes care of allocating parallel
resources and setting up the processes such that they can communicate
with one another.

We can run it on the login node using four parallel processes with

```
$ mpirun -n 4 ./hello
```

{{< hint warning >}}

You should not use the login node for large-scale computation, but
instead use a batch script and submit to the batch system. You should
also use the batch system when benchmarking.

{{< /hint >}}

If we want to submit to the backend, we need to write a batch script

{{< code-include "parallel/hello/hello.slurm" "sh" >}}


{{< hint "info" >}}

On some systems you need to specify the number of processes you want
to use when executing `mpirun`. However, on Hamilton, the metadata in
the scheduler is used to determine the number of processes. Here we
request 1 node and 24 tasks per node.

Hence you should only explicitly specify if you want to run with an
amount of parallelism different to that specified in your submission
script.
{{< /hint >}}

{{< question >}}

Try running on two compute nodes, by changing the `--nodes=1` line to
`--nodes=2` in the batch script. How many total processes do you now
have? What do you notice about the node names?

{{< /question >}}

## A Python version

If you've installed [mpi4py](http://mpi4py.readthedocs.io), you can
also run the Python equivalent.

{{< code-include "parallel/hello/hello.py" "py" >}}

This time we run with

```
mpirun -n 4 python hello.py
```
