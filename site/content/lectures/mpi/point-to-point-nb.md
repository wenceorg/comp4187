---
title: "Non-blocking point-to-point messaging"
katex: true
weight: 2
---

# Non-blocking messages

As well as the blocking point to point messaging we saw [last
time]({{< ref "point-to-point.md" >}}), MPI also offers _non-blocking_
versions.

These functions all return immediately, and provide a "request" object
that we can then either wait for completion with or inspect to check
if the message has been sent/received.

The function signatures for
[`MPI_Isend`](https://rookiehpc.com/mpi/docs/mpi_isend.php) and
[`MPI_Irecv`](https://rookiehpc.com/mpi/docs/mpi_irecv.php) are:

```c
int MPI_Isend(const void *buffer, int count, MPI_Datatype dtype, int dest, int tag, MPI_Comm comm, MPI_Request *request);
int MPI_Irecv(void *buffer, int count, MPI_Datatype dtype, int dest, int tag, MPI_Comm comm, MPI_Request *request);
```
The mpi4py versions are:
```py
request = comm.Isend([buffer, count, datatype], dest, tag)
request = comm.Irecv([buffer, count, datatype], src, tag)
```

So both sends and receives now _return_ a request object.


{{< hint warning >}}

With the [blocking versions]({{< ref "point-to-point.md" >}})
(`MPI_Send`, `MPI_Ssend`, `MPI_Bsend`), the buffer argument is safe to
reuse _as soon as the function returns_. Equally, as soon as
`MPI_Recv` returns, we know the message has been received and we can
inspect the contents.

**This is not the case** for non-blocking calls.

We are not allowed to reuse the buffer (or rely on its contents being
ready) until we have "waited" on the `request` handle.

See below for details on how to do this.

{{< /hint >}}

If we have a request, we can check whether the message it corresponds
to has been completed with [`MPI_Test`](https://rookiehpc.com/mpi/docs/mpi_test.php)

```py
request.Test()
=> True  # if the request is completed (message is sent/received)
=> False # otherwise.
```

The return value will be true if the provided request has been
completed, and false otherwise.

If instead we want to wait for completion, we can use
[`MPI_Wait`](https://rookiehpc.com/mpi/docs/mpi_wait.php)

```py
request.Wait(self, Status status=None)
```

Which waits until the message corresponding to `request` has been
completed.

Both of these calls can _complete_ the message exchange. If `MPI_Test`
returns `True`, the message has been sent/received
and the user-provided send/receive buffer is safe to be used again.

Here's a picture of a non-blocking `MPI_Issend` matching with a
blocking `MPI_Recv`. Note how the data transfer does not start
(because this is a synchronous send) until the matching receive has
been posted (set up). So the first `MPI_Test` returns false. The
`MPI_Wait` will return immediately because the message has now been
transferred.

{{< manfig
    src="mpi-issend-cartoon.svg"
    width="75%"
    caption="A non-blocking synchronous send returns immediately, and the data transfer begins as soon as the matching receive appears." >}}

## Why would you do this?

Non-blocking messages allow us to separate "posting" messages
from when we check if they are completed. One reason to do this is
that MPI libraries often have optimisations to complete sends quickly
if the matching receive already exists.

If I am receiving messages from 10 different processes, if I use
a blocking `MPI_Recv`, then there is only ever one receive ready at
any one time. Conversely if I use `MPI_Irecv`, then all receives will
be ready, and the MPI library can complete them as the matching send
arrives.

It also allows us to simplify programs that exchange many messages if
we're trying to avoid deadlocks. We can just post all sends/receives
at once and then wait, rather than having to arrange that we have a
single send/receive ready at the right time.

Finally, non-blocking communication allows us to (in theory) _overlap_
communication with computation. This can help to improve scaling
performance in some cases.

As you probably saw when doing the [ping-pong]({{< ref
"pingpong.md" >}}) exercise, all MPI messages have a non-zero
latency. That means that no matter how small it is, it takes some
time for a message to cross the network. If we use blocking messages,
the best case total time for our simulation is going to be

$$
T_{\text{compute}} + T_{\text{communicate}}
$$

Many scientific computing simulations have compute and communication
parts that can _overlap_. For example, when domain decomposing a mesh
for a parallel PDE solver, most of the computation can be done
without communicating with our neighbours: we only need information
when we're near the edge of our local domain. We can therefore often
split the simulation into phases:

1. Send data to neighbours
1. Compute on local data that doesn't depend on neighbours
1. Receive data from neighbours
1. Compute on remaining local data

If we use non-blocking messages, we can sometimes hide the latency in
steps (1) and (3), so that the total simulation time is now

$$
\max(T_{\text{compute}}, T_{\text{communicate}}) < T_{\text{compute}} + T_{\text{communicate}}
$$

The implementation of halo exchanges in the Grid data structure will
use this facility.


## Waiting for multiple messages

The advantage of the non-blocking communication mode becomes more
apparent when we look at waiting or testing for completion of multiple
messages simultaneously.

A typical pseudo-code with non-blocking communication might look
something like this

```py
requests = []
for _ in range(nrecv):
    requests.append(comm.Irecv(...))

for _ in range(nsend):
    requests.append(comm.Isend(...))

# Some work that doesn't depend on the messages
...

```

Having done the work that doesn't depend on messages, we now need to
wait for message completion.

Perhaps we need all the messages to complete, in which case we can use
[`MPI_Waitall`](https://rookiehpc.com/mpi/docs/mpi_waitall.php)

```c
MPI.Request.Waitall(requests)
```

This approach is preferred over a loop calling `MPI_Wait` on each
request, since the MPI implementation is free to process the arriving
messages in any order when we call `MPI_Waitall` which might speed
things up.

Perhaps we just want a message to have arrived, in which case we can
use [`MPI_Waitany`](https://rookiehpc.com/mpi/docs/mpi_waitany.php)

```py
which = MPI.Request.Waitany(requests)
```

Now the `which` variable tells us which of the requests completed.

Finally, suppose we want to wait until _at least one_ message has
completed, we can use
[`MPI_Waitsome`](https://rookiehpc.com/mpi/docs/mpi_waitsome.php)

```py
indices = MPI.Request.Waitsome(requests)
# Now len(indices) tells us how many requests are completed,
# and indices[0..nfinished-1] tells us which requests they are
```

There are also matching
[`MPI_Testall`](https://rookiehpc.com/mpi/docs/mpi_testall.php),
[`MPI_Testany`](https://rookiehpc.com/mpi/docs/mpi_testany.php), and
[`MPI_Testsome`](https://rookiehpc.com/mpi/docs/mpi_testsome.php)
calls which don't block for completion of the messages.

A high quality MPI implementation will provide optimised code for
these routines that is more efficient than a loop with
`MPI_Test`/`MPI_Wait` pairs.

{{< exercise >}}
### Gathering data from every process

Write an MPI code in which rank-0 gathers a message from every process
and places it in an array at a position corresponding to the rank of
the sender.

So if running with $P$ processes, rank-0 should allocate an array with
space for $P$ entries, and after collecting the messages.

Compare the performance of two versions.

1. rank-0 uses a blocking `MPI_Recv` for all receives
2. rank-0 uses non-blocking `MPI_Irecv` followed by `MPI_Waitall`.

Which performs better as a function of the total number of messages, $P$?

{{< /exercise >}}

## Wildcard matching {#wildcards}

So far, we've always specified specific `source` and `tag` arguments in
the arguments to `MPI_Recv` and `MPI_Irecv`. MPI also provides us with
the option to say "receive a message, I don't care who its from, or
what the tag is".

We do that by providing `MPI_ANY_SOURCE` and/or `MPI_ANY_TAG` as the
source and tag arguments respectively.

We can subsequently, find out where we got the message from, and what
its tag was, by inspecting the `status` object that `MPI_Recv`
returns.

Up to now, we've just said `MPI_STATUS_IGNORE`, but we can also do

```py
status = MPI.Status()
comm.Recv(..., MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)

status.source                   # The source rank
status.tag                      # The tag
```

There actually aren't that many reasons you would use wildcards in
receives. They can be useful when implementing [dynamic sparse data
exchange](http://htor.inf.ethz.ch/publications/index.php?pub=99).

{{< hint info >}}
Typically, the implementation of "wildcard" matching is less efficient
than message matching with given source and tag arguments.
{{< /hint >}}

## Summary

As well as providing blocking send/receive options, MPI provides
non-blocking versions.

These allow us to potentially improve performance of message exchange,
and simplify writing algorithms that need to match many pairs of
messages, without thinking as hard about potential deadlocks.

The critical thing to recall is that **we are not allowed** to look at
the buffers we pass into non-blocking sends/receives until after
calling a blocking `MPI_Wait`-like call, or a non-blocking
`MPI_Test`-like call has returned true.
