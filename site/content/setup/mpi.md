---
title: "MPI"
weight: 2
---
# Options for running MPI programs

For the larger parallel runs in the course, and benchmarking, we will
use the [Hamilton](https://www.dur.ac.uk/cis/local/hpc/) cluster. You
may wish to do development on your own machine. I provide some brief
guidance on what you need in terms of appropriate compilers and MPI
implementations.


## Hamilton access and quickstart

If you don't already have an account on Hamilton, please register for
one by [following their
instructions](https://www.dur.ac.uk/cis/local/hpc/hamilton/account/#getting_account).

When requesting an account, please put "Lawrence Mitchell" as the
approver, and mention that the access if for the Computer Science
course COMP4187.

We'll learn more on how to use Hamilton by doing the various
exercises, but you may wish to look at this brief [quickstart
guide](https://teaching.wence.uk/phys52015/setup/hamilton-quickstart/#supercomputing-durham-hamilton-quick-start-guide). 

## MacOS

I recommend [homebrew](https://brew.sh) for installing packages on
MacOS. You will need an MPI implementation, for which I recommend
[mpich](https://www.mpich.org), which can be obtained with

```
$ brew install mpich
```

This will also set up the necessary C compilers (the Apple toolchain
provides these via clang).

## Linux-based systems

On Debian-based systems you'll need the following `apt` packages

```
build-essential
libmpich-dev
mpich
gcc
```

## Windows

Microsoft provides an MPI implementation called
[MS-MPI](https://docs.microsoft.com/en-us/message-passing-interface/microsoft-mpi),
but I have no experience of it, or development on Windows.

## Python interface to MPI

Having installed the MPI and compiler toolchain, it is also possible
to install Python bindings to MPI, called
[mpi4py](https://mpi4py.readthedocs.io). 

I recommend doing it in a virtual environment and then you can use

```
pip install mpi4py
```

(Or your other favourite python package manager).
