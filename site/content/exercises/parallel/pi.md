---
title: "Calculating π"
weight: 2
katex: true
---

# Simple MPI parallelism

In this exercise we're going to compute an approximation to the value
of π using a simple Monte Carlo method. We do this by noticing that if
we randomly throw darts at a square, the fraction of the time they
will fall within the incircle approaches π.

Consider a square with side-length $2r$ and an inscribed circle
with radius $r$.

{{< manfig src="square-circle.svg" 
    width="40%"
    caption="Square with inscribed circle" >}}

The ratio of areas is

$$
\frac{A_\text{circle}}{A_\text{square}} = \frac{\pi r^2}{4 r^2} = \frac{\pi}{4}.
$$

If we therefore draw $X$ uniformly at random from the distribution
$\mathcal{U}(0, r) \times \mathcal{U}(0, r)$, then the
probability that \\(X\\) is in the circle is

$$
p_\text{in} = \frac{\pi}{4}.
$$

We can therefore approximate π by picking $N_\text{total}$ random
points and counting the number, $N_\text{circle}$, that fall within the
circle

$$
\pi_\text{numerical} = 4 \frac{N_\text{circle}}{N_\text{total}}
$$

## Obtaining the code

The code for this exercise lives in the `code/parallel/pi/`
subdirectory in the [repository]({{< repo >}}), as `pi.py`.

{{< details "Working from the repository" >}}

I recommend working on a branch in your clone of the repository, so
that you can commit any changes you make and experiments you do.

{{< /details >}}

I provide a simple serial implementation that uses numpy to generate
the random numbers.

{{< exercise >}}

Adapt the code so that it runs for a range of different choices of the
number of samples, `N`. Plot the error in the estimated value of $\pi$
as a function of `N`.

What relationship do you observe between the accuracy of the
approximate result and `N`?

{{< details Hint >}}
A double-precision approximation to $\pi$ is available as `numpy.pi`.
{{< /details >}}

{{< /exercise >}}

## Parallelisation with MPI

We're now going to parallelise this computation with MPI. 

{{< hint info >}}
If you're running on Hamilton don't forget to load the right modules

```
python/3.6.8
gcc/8.2.0
intelmpi/gcc/2019.6
```
{{< /hint >}}


The code already imports `mpi4py`, but does not distribute the work.

{{< exercise >}}

Adapt the `run` function so that the total samples are (approximately)
evenly distributed between all the ranks in the given communicator.

You'll now have each process computing a partial answer, so combine
them with
[`MPI_Allreduce`](https://rookiehpc.com/mpi/docs/mpi_allreduce.php).

{{< /exercise >}}

### Parallelising the random number generation

Running this code in parallel presents us with a slight problem. We
need to think about how to provide statistically independent random
number streams on the different processes.

Fortunately, modern versions of numpy have us covered. Their
documentation describes how to obtain [random numbers in
parallel](https://numpy.org/doc/stable/reference/random/parallel.html).

{{< exercise >}}

Replace the use of the `default_rng` generator with a Generator that
will produce a different stream on each process. Remember that the
`comm.rank` is unique to each process in the communicator.

{{< /exercise >}}

### Benchmarking

We'll now briefly look at how this code scales, by carrying out some
simple strong and weak scaling tests.

{{< exercise >}}

Use `MPI.Wtime()` to measure the length of time the `run` function
takes on each process.

Use the maximum over all processes for your plots.

1. Produce a strong scaling plot using a total of $N=10^8$ points.
2. Produce weak scaling plots using $N=10^4$, $N=10^5$, $N=10^6$, and
   $N=10^7$ points per process.
   
What observations do you make about the scaling behaviour?

{{< /exercise >}}
