---
title: "1-D domain decomposition"
weight: 3
katex: true
---

# Domain decomposition and data parallelism

In this exercise, we're going to look at some of the implementation
steps involved in domain-decomposing a finite difference computation.

The particular case we are going to consider is that of edge detection
in grayscale images, and subsequent reconstruction of the original
image from the detected eges.

## Introduction and background

A particularly simple way of detecting the edges in an image is to
convolve it with a [Laplacian
kernel](https://aishack.in/tutorials/sobel-laplacian-edge-detectors/).
That is, given some image $I$, we can obtain its edges with

$$
E = \nabla^2 I.
$$

By now, you should be familiar with the [five-point finite
difference stencil](https://en.wikipedia.org/wiki/Five-point_stencil),
which we'll use heree for discretisation.


Having computed the edges, $E$, we can (approximately) reconstruct the
image $I$ by applying the inverse $\left(\nabla^2\right)^{-1}$. The
approximate reconstructed image is

$$
I^r = \left(\nabla^2\right)^{-1} E.
$$

We discretise the image as a 2D array, computing the edges can be done
in one step

$$
E_{i, j} = I_{i-1, j} + I_{i+1, j} + I_{i, j-1} + I_{i, j+1} - 4I_{i,j}
$$

for all pixels $i, j$ in the image.

To reconstruct the image, we will use a [Jacobi
iteration](https://en.wikipedia.org/wiki/Jacobi_method), given an
initial guess for the reconstructed image, $I^{r, 0}$, we set
$k = 0$ and then an improved guess is given by

$$
I_{i,j}^{r,k+1} = \frac{1}{4}\left(I_{i-1, j}^{r,k} + I_{i+1,j}^{r,k} +
I_{i,j-1}^{r,k} + I_{i,j+1}^{r,k} - E_{i,j}\right)
$$
for all pixels $i, j$ in the image. You'll note that this is exactly
the Jacobi smoother we saw last term.

After many many iterations ($k \to \infty$), this will converge to a
good approximation to the initial image.

{{< hint danger >}}

**WARNING, WARNING**. As we saw last term when looking at multigrid
methods, this is a _terrible_ way of inverting the
Laplacian, we're using it to illustrate some domain decomposition and
parallelisation approaches: the multilevel stuff is to come!

{{< /hint >}}

## Implementation

This code lives in the `code/parallel/dd-image/` subdirectory. There
are some sample images in the `images` subdirectory.

### Data structures

The image itself is stored as a 2D array. We use domain decomposition
to divide up the global image between processes. Here we are only
using a 1-D decomposition (which is slightly easier to program, but
less efficient). In real life you'd use a 2-D decomposition.

The idea is that each process owns a contigous slice of the total
image. To compute the stencil that updates each pixel in the image, we
need to access neighbouring values. On the global image boundary,
we'll use zero Dirichlet conditions. Where two processes meet, they
will have to communicate to exchange values.

{{< columns >}}
{{< manfig src="image-two-ranks.svg"
    width="100%"
    caption="Decomposition of a 2D image between two processes. " >}}
<--->
{{< manfig src="image-two-ranks-split.svg"
    width="82%"
    caption="Decomposition of a 2D image showing separation of memory"
    >}}
{{< /columns >}}

The nice way of thinking about this is to separate the communication
and computation phases using _global_ and _local_ vectors. _Global_
vectors represent the process's portion of the image which it is
responsible for updating. _Local_ vectors are padded with values from
either the Dirichlet data or the neighbouring process, so that we can
compute on them without needing to communicate, or insert conditional
branches in the inner loop.

A computation phase, to reconstruct the image from edges is, in
pseudo-code, something like:

```python
def update(uold, unew):
    """Update unew <- stencil(uold)

    Both uold and unew are global vectors
    """
    ulocal = global_to_local(uold)
    ulocalnew = apply_stencil(ulocal)
    unew = local_to_global(ulocalnew)
    return unew
```

To implement this, we need to carry around information about the grid
that decomposes the global image.

The `global_to_local` and `local_to_global` calls communicate halo (or
ghost) values between processes. The `apply_stencil` then operates on
purely local data (it just has to iterate over the correct part of the
image).

### Data distribution and parallelisation

There are three steps to the parallelisation of the code.

1. Having read the image on a single process, distribute across all
   the processes in the communicator;
2. Run the edge detection, and then reconstruction routines (using the
   ideas described above);
3. Gather the distributed, reconstructed, image to a single rank to
   write the output.
   
{{< hint info >}}

For really large-scale computations, it is best to use parallel
output, but we're not going to do that here.

{{< /hint >}}


The template code implements this algorithmic workflow, but has
stubbed out a bunch of the functions. Your job is to implement the
different pieces and put it together.

{{< exercise >}}

Implement distribution of the image array across the available
processes. You should use
[`MPI_Scatter`](https://rookiehpc.com/mpi/docs/mpi_scatter.php) or
[`MPI_Scatterv`](https://rookiehpc.com/mpi/docs/mpi_scatterv.php)
depending on whether the number of processes evenly divides the number
of image rows or not.

{{< /exercise >}}

With this step done, you should be able to run in parallel and see the
different outputs. Note that at this point, the boundary values will
be incorrect. So our next step is to implement the correct
`global_to_local` and `local_to_global` routines.

{{< exercise >}}

Use [non-blocking]({{< ref "point-to-point-nb.md" >}}) sends and
receives to implement the data exchange necessary to update ghost
values in `global_to_local` and `local_to_global`. Think about where
you need to actually transfer data: do you need to do message exchange
in both routines, or can you get away with local copies for one of
them?

{{< details Hint >}}

For these kind of things, I always find it helpful to draw some
pictures of where the data live.

{{< /details >}}

{{< /exercise >}}


Finally we need to gather the resulting images onto a single rank for
writing. Having implemented the distribution by scattering data, this
should be reasonably straightforward: it's the inverse operation,
using [`MPI_Gather`](https://rookiehpc.com/mpi/docs/mpi_gather.php) or
[`MPI_Gatherv`](https://rookiehpc.com/mpi/docs/mpi_gatherv.php) as
appropriate.
