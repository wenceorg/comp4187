---
title: "Ping-pong latency"
weight: 4
katex: true
---

# Measuring point-to-point message latency with ping-pong

In this exercise we will write a simple code that does a message
ping-pong: sending a message back and forth between two processes.

We can use this to measure both the _latency_ and _bandwidth_ of the
network on our supercomputer. Which are both important measurements
when we're looking at potential parallel performance: they help us to
decide if our code is running slowly because of our bad choices, or
limitations in the hardware.

## A model for the time to send a message

We care about the total time it takes to send a message, our model is
a linear model which has two free parameters:

1. $\alpha$, the message latency, measured in seconds;
2. $\beta$, the inverse network bandwidth, measured in seconds/byte
   (so that the bandwidth is $\beta^{-1}$.

With this model, the time to send a message with $b$ bytes is

$$
T(b) = \alpha + \beta b
$$

## Implementation

In the lectures, we wrote some code to do this in
[`code/parallel/live/pingpong.py`]({{< code-ref
"parallel/live/pingpong.py" >}}).

We need to run it with at least two processes, but you can run it in
serial with `-h` to see what options it takes

```
$ python pingpong.py -h
usage: pingpong.py [-h] [--use-pickle] output_file

positional arguments:
  output_file   Write data to specified numpy file (load with numpy.load)

optional arguments:
  -h, --help    show this help message and exit
  --use-pickle  Send messages using pickle interface?
                If False (default), send numpy buffers
```

When running, it prints some progress information about the size of
message it's sending to the screen and writes an output file of the
timing data in a format suitable for loading by
[`numpy.load`](https://numpy.org/doc/stable/reference/generated/numpy.load.html).
You can then load this and produce a plot with
[matplotlib](https://matplotlib.org).

## Experiment

{{< exercise >}}

Run the code using two processes on your own machine (or Hamilton
using a single node).

It will save the measured times in a commandline-specified file.

Produce a plot of the data, and try and fit the linear model to it.
What do you get for your values of $\alpha$ and $\beta$.

If you perform the same experiment using both the numpy interface for
sending data and the pickle interface (selected with the
`--use-pickle` argument), do you observe a difference in the
performance?

If yes, why do you think this might be? Recall that in the pickle
interface, mpi4py must first convert the buffer into its pickled form.
Is this free? Does this change the size of the buffer?
{{< /exercise >}}

{{< question >}}

Perform the same experiment, but this time, place the two processes on
_different_ Hamilton compute nodes. Do you observe a difference in the
performance?

To do this, you'll need to write a SLURM batch script that specifies

```sh
# Two nodes
#SBATCH --nodes=2
# One process per node
#SBTACH --ntasks-per-node=1
```

{{< /question >}}
