---
title: MPI
draft: false
weight: 2
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

We're going to do our programming in Python in this course so you'll
need the Python bindings to MPI,
[mpi4py](https://mpi4py.readthedocs.io).

Let's look at a simple ["Hello, World"]({{< ref "hello.md#mpi" >}})
MPI program.

{{< code-include "parallel/hello/hello.py" "py" >}}

MPI is a library-based programming model, so we start by importing the
library. If writing in C, we need to remember to call `MPI_Init`, but
mpi4py does that for us when we do

```py
from mpi4py import MPI
```

If we want to control what is going on, we should instead do

```py
import mpi4py
# See the documentation for valid arguments
mpi4py.rc(initialize=False)

from mpi4py import MPI
MPI.Init()
```

Similarly, the last thing we should do is call `MPI_Finalize`. By
default `mpi4py` does this for us by installing it in an
[`atexit`](https://docs.python.org/3/library/atexit.html) handler.

With those logistics out the way, it looks like our code doesn't
contain any parallelism at all. What's going on?

{{< hint info >}}

When I link to MPI functions in the documentation, the links will be
to C function declarations (since there's no official Python
documentation).

Here's a quick translation guide.

1. Functions that don't reference a communicator in the C interface
   (like [`MPI_Init`](https://rookiehpc.com/mpi/docs/mpi_init.php)),
   become functions on the `MPI` module. Capitalisation remains the
   same: `MPI.Init()`.
2. Functions that do reference a [communicator]({{< ref
   "#communicators" >}}) (like
   [`MPI_Send`](https://rookiehpc.com/mpi/docs/mpi_send.php)), become
   methods on the communicator: `communicator.Send()`.
3. There are two versions of all the messaging routines. The first set use
   the Python [pickle](https://docs.python.org/3/library/pickle.html)
   module to send arbitrary Python data (these are slow) and are spelt
   with a **lowercase** name (e.g. `communicator.send()`). The second
   set can only send objects that implement the Python [buffer
   protocol](https://www.python.org/dev/peps/pep-3118/), the usual
   case will be [numpy arrays](https://numpy.org), these are fast
   (because no copy is required) and are spelt with a **capitalised**
   name (e.g. `communicator.Send()`). See the [mpi4py
   tutorial](https://mpi4py.readthedocs.io/en/stable/tutorial.html#tutorial)
   for more information.

We'll revisit these concepts through the examples.

{{< /hint >}}

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

Like in OpenMP programming (which you saw last year), we achieve
parallelism by having many processes cooperate to solve the same task.
We must come up with some way of dividing the data and computation
between the processes.

Since processes do not share memory, they must instead send messages
to communicate information. This is implemented in MPI through library
calls that we can make from our sequential programming language.
This is in contrast to OpenMP which defines pragma-based extensions to
the language.

The core difficulty in writing message-passing programs is the
conceptual model. This is a very different model to that required for
sequential programs. Becoming comfortable with this model is key to
understanding MPI programs. A key idea, is that there is much more
focus on the _decomposition of the data and work_. That is, we must
think about how we divide the data (and hence work) in our parallel
program. I will endeavour to emphasise this through the examples and
exposition when we encounter MPI functions.

Although at first MPI parallelism seems complicated, it is, in my
experience, a really well-designed programming model, and well-suited
suited to the implementation of reusable software.

## Single program, multiple data (SPMD)

Most MPI programs are written using the single-program, multiple data
(SPMD) paradigm. All processes are launched and run their _own_ copy
of the same program. You saw this with the [Hello World]({{< ref
"hello.md" >}}) example.

{{< exercise >}}

If you've haven't already done it, go away and do that [hello world
exercise]({{< ref "hello.md" >}}) now, since it also sets up your
environment for the rest of the course.

{{< /exercise >}}

Although each process is running the same program, they each have a
separate copy of data.

So that this is useful, processes have a unique identifier, their
_rank_. We can then write code that sends different ranks down
different paths in the control flow.

The way to think about this is as if we had written a number of
different copies of a program and each process gets its own copy. They
then execute at the same time and can pass messages to each other.

Suppose we have a function

```py
def print_hello(comm):
    print("Hello, I am rank %d of %d", comm.rank, comm.size)
```

Then if we execute it with two processes we have

{{< columns >}}
Process 0

```py
def print_hello(comm):
    print("Hello, I am rank %d of %d",
          0, 2)
```
<--->

Process 1
```py
def print_hello(comm):
    print("Hello, I am rank %d of %d",
          1, 2)
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

[`MPI.COMM_WORLD`](https://rookiehpc.com/mpi/docs/mpi_comm_world.php)
: A communicator consisting of all the processes in the current run.

[`MPI.COMM_SELF`](https://rookiehpc.com/mpi/docs/mpi_comm_self.php)
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

This concept is illustrated by [`parallel/snippets/comm-world-self.py`]({{<
code-ref "parallel/snippets/comm-world-self.py" >}}).


Run with
```
$ mpirun -n 4 python comm-world-self.py
```

Do you understand the output?

{{< hint info >}}
Don't forget to load the correct `intelmpi/gcc/2019.6` module, along
with activating your virtual environment.
{{< /hint >}}

{{< /exercise >}}

An important thing about communicators is that they are always
explicit when we send messages: to send a message, we need a
communicator. So communicators, and the group of processes they
represent, are at the core of MPI programming.
