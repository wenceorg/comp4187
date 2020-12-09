---
title: MPI
draft: false
weight: 11
---

# MPI: a messaging API

If we want to solve really big problems (maybe upwards of 50 million
degrees of freedom), we run into the issue that our problem likely
doesn't fit (or is too slow) on a single shared memory system.
We therefore need to move to a parallelisation model with
_distributed memory_.

In this situation, we have multiple computers which are connected with
some form of network. The dominant parallel programming paradigm for
this situation is that of _message passing_.

In distributed memory settings we need to explicitly package up and
send data between the different computers involved in the computation.

In the high performance computing world, the dominant library for
message passing is [MPI](https://www.mpi-forum.org/), the Message
Passing Interface.

Let's look at a simple ["Hello, World"]({{< ref "hello.md#mpi" >}})
MPI program.

{{< code-include "parallel/hello/hello.c" "c" >}}

Our MPI programs always start by initialising MPI with `MPI_Init`.
They must finish by shutting down, with `MPI_Finalize`. Inside, it
seems like there is no explicit parallelism written anywhere.

## Concepts

The message passing model is based on the notion of processes (rather
than the threads in OpenMP). Processes are very similar, but do not
share an address space (and therefore do not share memory).

{{< columns >}}

{{< manfig
    src="processes-private-memory-sketch.svg"
    width="100%"
    caption="Processes do not share memory." >}}

<--->
{{< manfig
    src="shared-memory-sketch.svg"
    width="100%"
    caption="Threads can share memory." >}}

{{< /columns >}}

Like in OpenMP programming, we achieve parallelism by having many
processes cooperate to solve the same task. We must come up with some
way of dividing the data and computation between the processes.

Since processes do not share memory, they must instead send messages
to communicate information. This is implemented in MPI through library
calls that we can make from our sequential programming language.
This is in contrast to OpenMP which defines pragma-based extensions to
the language.

The core difficulty in writing message-passing programs is the
conceptual model. This is a very different model to that required for
sequential programs. Becoming comfortable with this model is key to
understanding MPI programs. A key idea, which is different from the
examples we've seen with OpenMP, is that there is much more focus on
the _decomposition of the data and work_. That is, we must think about
how we divide the data (and hence work) in our parallel program. I
will endeavour to emphasise this through the examples and exposition
when we encounter MPI functions.

Although at first MPI parallelism seems more complicated than OpenMP
(we can't just annotate a few loops with a `#pragma`), it is, in my
experience, a much more _powerful_ programming model, and better
suited to the implementation of reusable software.

## Single program, multiple data (SPMD)

Most MPI programs are written using the single-program, multiple data
(SPMD) paradigm. All processes are launched and run their _own_ copy
of the same program. You saw this with the [Hello World]({{< ref
"hello.md" >}}) example.

Although each process is running the same program, they each have a
separate copy of data (there is no sharing like in OpenMP).

So that this is useful, processes have a unique identifier, their
_rank_. We can then write code that sends different ranks down
different paths in the control flow.

The way to think about this is as if we had written a number of
different copies of a program and each process gets its own copy. They
then execute at the same time and can pass messages to each other.

Suppose we have a function

```c
void print_hello(MPI_Comm comm)
{
  int rank;
  int size;

  MPI_Comm_rank(comm, &rank);
  MPI_Comm_size(comm, &size);

  printf("Hello, I am rank %d of %d\n", rank, size);
}
```

Then if we execute it with two processes we have

{{< columns >}}
Process 0

```c
void print_hello(MPI_Comm comm)
{
  int rank;
  int size;

  rank = 0;
  size = 2;
  printf("Hello, I am rank %d of %d\n", rank, size);
}
```
<--->

Process 1
```c
void print_hello(MPI_Comm comm)
{
  int rank;
  int size;

  rank = 1;
  size = 2;
  printf("Hello, I am rank %d of %d\n", rank, size);
}
```

{{< /columns >}}

Of course, on its own, this is not that useful. So the real power in
MPI comes through the ability to send messages between the processes.
These are facilitated by communicators.

## Communicators

The powerful abstraction that MPI is built around is a notion of a
communicator. This logically groups some set of processes in the MPI
program. All communication happens via communicators. That is, when
sending and receiving messages we do so by providing a
communicator and a source/destination to be interpreted with reference
to that communicator.

When MPI launches a program, it pre-initialises two communicators

`MPI_COMM_WORLD`
: A communicator consisting of all the processes in the current run.

`MPI_COMM_SELF`
: A communicator consisting of each process individually.

The figure below shows an example of eight processes and draws the
world and self communicators.

{{< manfig
    src="comm-world-comm-self.svg"
    width="75%"
    caption="An MPI program with eight processes and their ranks in `MPI_COMM_WORLD` (left) and `MPI_COMM_SELF` (right). In the right-hand figure the corresponding world rank is shown in parentheses" >}}

A key thing to note is that the processes are the _same_ in the left
and right figures. It is just their identifier that changes depending
on which communicator we view them through.

{{< exercise >}}

This concept is illustrated by [`mpi-snippets/comm-world-self.c`]({{<
code-ref "mpi-snippets/comm-world-self.c" >}}).

Compile it with

```
$ mpicc -o comm-world-self comm-world-self.c
```

{{< details Hint >}}

Don't forget than in addition to loading the normal compiler modules
you also need to load the `intelmpi/intel/2018.2` module.

{{< /details >}}

And run with
```
$ mpirun -n 4 ./comm-world-self
```

Do you understand the output?

{{< /exercise >}}

An important thing about communicators is that they are always
explicit when we send messages: to send a message, we need a
communicator. So communicators, and the group of processes they
represent, are at the core of MPI programming. This is in contrast to
OpenMP where we generally don't think about which threads are in
involved in a parallel region.

