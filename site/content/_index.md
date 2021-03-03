---
title: Introduction
draft: false
katex: true
weight: 1
---

# COMP4187: Parallel Scientific Computing II

This is the course webpage for [COMP4187]({{< modulepage >}}). It
collects the exercises, syllabus, and notes. The source repository is
[hosted on GitHub]({{< repo >}}).

This submodule builds on Numerical Algorithms I (Parallel Scientific
Computing I) and introduces advanced topics in ODE integration
schemes, and spatial discretisation.

## Syllabus

### Numerical Methods (Term 1)

Topic 1: Spatial discretisation. Finite difference methods for partial differential equations (PDEs), stability, convergence, and consistency;

Topic 2: Time dependent PDEs. Stability constraints for time-dependent PDEs, connection to eigenvalue analysis;

Topic 3: Implicit ordinary differential equation (ODE) methods, and matrix representations of PDE operators;

Topic 4: Advanced algorithms for PDEs. Fast methods of solving PDEs, high order discretisation schemes.

### Parallel Computing (Term 2)

- Distributed memory programming models: [MPI](https://www.mpi-forum.org).

- Parallel algorithms and data structures for finite difference codes.

- Irregular data distribution and load-balancing.

- Measurement and modelling. Analysis of achieved performance,
  performance models, including the Roofline model.

### Discussion forum

I have set up a [discussion forum]({{< repo >}}/discussions) where you
can ask, and answer, questions. You'll need a
[GitHub](https://github.com) account to use it, but you've all got one
of those already, right? Note that this repository and forum is
publically visible.

### Office hours

No formal office hours, please [email
me](mailto:lawrence.mitchell@durham.ac.uk) to arrange something.

### Lecture scribblings and video links

I'll add the annotated scribblings, live code examples, and links to
the videos (accessible with a Durham account) here.

- 2021-01-13: [Scribbles]({{< static-ref "parallel/2020-21/lec01.pdf"
  >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=fe338448-89f7-49b6-be1b-acaf00a72ad7),
  [code]({{< code-ref "parallel/live/hello.py" >}})
- 2021-01-20: [Scribbles]({{< static-ref "parallel/2020-21/lec02.pdf"
  >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=ef0fb74d-cd43-4670-93be-acb600a5e14d)

  About half way through when I wrote down the efficiency for weak
  scaling I simplified $\frac{T_1}{T_1 + \mathcal{o}(p)T_1}$ to $\frac{T_1}{1 + \mathcal{o}(p)}$. The correct efficiency for weak scaling is
  $$
  \eta_p = \frac{1}{1 + \mathcal{o}(p)},
  $$
  the correct expressions for $\eta_p^{\text{fix}}$ and
  $\eta_p^{\text{log}}$ are therefore

  {{< rawhtml >}}
  $$
  \begin{aligned}
  \eta_p^{\text{fix}} &= \frac{1}{1 + \alpha}\text{ and} \\
  \eta_p^{\text{log}} &= \frac{1}{1 + \mathcal{O}(\log p)}.
  \end{aligned}
  $$
  {{< /rawhtml >}}

  I've updated the notes that were uploaded to reflect this, but
  can't change the video. The subsequent discussion of what the plots
  look like is, I think, all correct.

  Some more detail on parallel scaling laws can be [found
  here](https://teaching.wence.uk/phys52015/notes/theory/scaling-laws/).

  For details on machine (or algorithmic) scaling, and its application
  to PDE solvers, I like [_A performance spectrum for parallel
  computational frameworks that solve
  PDEs_](https://arxiv.org/pdf/1705.03625) (the published paper is [in
  CCPE](https://onlinelibrary.wiley.com/doi/abs/10.1002/cpe.4401)).
- 2021-01-27: [Scribbles]({{< static-ref "parallel/2020-21/lec03.pdf"
  >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=45ef144c-596e-4ef7-a140-acbd00a56638),
  [code]({{< code-ref "parallel/live/pingpong.py" >}})

  Have a go at running this code on your own machine (or on Hamilton).
  If on Hamilton do you observe different behaviour when running
  across more than one node? See [this exercise description]({{< ref
  "pingpong.md" >}}) for more information.

  The paper I briefly mentioned in the lecture is [_Scaling Limits for
  PDE-based
  simulation_](http://www.mcs.anl.gov/papers/P5347-0515.pdf), it goes
  into more details of what I was discussing the lecture with regards
  to turning machine and computational models into models for scaling.
  I'll cover a little more of it next week, so if you have time to
  skim through that would be great.
- 2021-02-03: [Scribbles]({{< static-ref "parallel/2020-21/lec04.pdf"
  >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=dc7a8f75-b76d-4f5d-95e9-acc400a73ecb)

  We looked at some results from the ping-pong code we wrote last
  time, and then discussed the idea that the reason we can have a hope
  of solving PDEs in parallel is that we have _sparse_
  representations. So we don't need to do alltoall communication and
  computation. We then started on how might divide the work on our
  grids up between parallel processes, with a goal of having
  $\frac{N}{P}$ work per process and (hopefully) at worst
  $\mathcal{O}(\log P)$ algorithmic, memory footprint, or
  message-passing complexity as a function of the number of processes.
  I tried to motivate why this is a reasonable goal for multigrid
  solvers.
- 2021-02-10: [Scribbles]({{< static-ref "parallel/2020-21/lec05.pdf"
  >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=4f9c54be-8651-4805-9935-accb00a87468)

  We briefly recapped why we want "square" subdomains: since we want
  to minimise surface to volume ratio. Then we started looking at the
  design of MPI-parallel grids. In particular, we motivated that we
  want to agglomerate messages into large batches (rather than sending
  many small messages).

  The key point in the design is the separation of "global" vectors
  (which have no overlap) which our timestepper wants to see, and
  "local" vectors (with overlap) which are necessary for computing (I
  called this assembly) the residual. The local vectors need overlap
  because the stencil doesn't just act pointwise. I sketched a
  plausible design for how this works, which we'll make more concrete
  next week.

  Next time we want to look at the analysis of scaling limits for
  Jacobi iteration from [_Scaling Limits for
  PDE-based
  simulation_](http://www.mcs.anl.gov/papers/P5347-0515.pdf), so

  {{< exercise >}}
  Please read the introduction and up to the send of Section II.B.1
  (Jacobi iteration) from that paper, we'll try and discuss the key
  points.
  {{< /exercise >}}
- 2021-02-17: [Scribbles]({{< static-ref "parallel/2020-21/lec06.pdf"
  >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=c8155b70-fde8-4d09-9d59-acd200a7b739)

  This time my annotatations where on the Fischer et al. paper I set
  as reading work. I provided some background on the application areas
  they are starting from (and nearly managed, up to one sign error, to
  get the [Navier--Stokes
  equations](https://en.wikipedia.org/wiki/Navier–Stokes_equations)
  correct). We then looked a little bit more at scaling models and did
  an analysis (following the paper) of scaling limits for a finite
  difference discretisation of the Laplacian in 3D if using Jacobi
  iterations as a solver. Each iteration is scalable, but since we
  need to do a number of iterations that increases with the total
  number of degrees of freedom, Jacobi iteration on its own is not
  algorithmically scalable. I got a bit confused with the way they had
  written the Jacobi update. There is a sign error in that equation.
  The uploaded scribbles work out what it should look like (in two
  different ways).

  The paper also presents the results of a detailed analysis (not
  worked through) for scaling limits for a V(1, 0) cycle of geometric
  multigrid. This _is_ an algorithmically scalable algorithm. It has
  more communication, with a term that grows with $\log P$, so as we
  add more processes we need more local work to remain computationally
  scalable.

  We remarked briefly on how few extra flops multigrid needs (compared
  to Jacobi iteration) to get a scalable algorithm.

  One thing I remarked on in Table 1 from the paper is exactly how
  fast the network interconnect is on nice HPC platforms. To see
  exactly how fast, compare with the latency for modern [NVMe
  SSDs](https://www.anandtech.com/show/16458/2021-ssd-benchmark-suite/3),
  which are touted as a real step forward in disk technology, and
  notice that we've had interconnects with lower latency than modern
  SSDs since _1990_.

  Next time we'll do some more hands on stuff and sketch some code
  for multi-level algorithms in MPI.
- 2021-02-24: [Scribbles (quite short)]({{< static-ref "parallel/2020-21/lec07.pdf"
  >}}), [code]({{< code-ref "parallel/live/Lec07.py" >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=2e211aac-bc6e-4d75-ac62-acda00b4ba0b)

  I introduced what we're doing for the coursework, a [candidate]({{<
  ref "coursework.md" >}}) is available, which may get minor textual
  edits after checking but is basically complete. We will be using
  [github classroom](https://classroom.github.com) to manage the code
  submission so please sign up via the link on the coursework page.

  For the remainder of the lectures, I'll be introducing concepts, and
  use, of the [PETSc](https://www.mcs.anl.gov/petsc/) library. PETSc
  is a sophisticated parallel library that provides many useful
  datastructures for PDEs on grids and unstructured meshes. We're
  using it provide the parallel grids and sparse matrices in the
  coursework, so you'll want to get it installed locally. If you have
  any issues here please **get in touch**.

  I started by introducing PETSc's
  [`Vec`](https://www.mcs.anl.gov/petsc/petsc-current/docs/manualpages/Vec/index.html)
  object. We saw that every PETSc object gets created with a
  communicator. Many of the operations are then _logically collective_
  over that communicator: all ranks must participate for correctness,
  even if there is no obvious synchronisation required.

  Most of the operations we saw were local (pointwise) operations on
  vectors, but the final thing we saw showed how PETSc deals with the
  problem of "batching" communication. If I want to set values in part
  of a `Vec` that I don't own, then I do that by first
  (non-collectively) calling `vec.setValues`. This internally creates
  a stash for the data that will need to be communicated. Once
  everyone is done setting values, there's a split-phase communication
  round with `vec.assemblyBegin()` followed by `vec.assemblyEnd()`.
  After the latter call, the `Vec` contains the new values and is
  ready to be used again.

  See the [commented code]({{< code-ref "parallel/live/Lec07.py" >}})
  for more details.
- 2021-03-03: [Scribbles]({{< static-ref "parallel/2020-21/lec07.pdf" >}}),
  [code]({{< code-ref "parallel/live/Lec08.py" >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=8189711a-b11b-4018-a694-ace000ab310c),
  
  We discussed sparse matrices, and a little bit about sparse matrix
  formats. I (somewhat informally) defined what we mean by a sparse
  matrix. We also briefly looked at how sparse matrices are
  distributed in parallel. This is interesting when we think about
  operations involving matrices and vectors, particularly we need that
  the parallel decomposition is _compatible_ (PETSc will complain if
  not). Matrices, representing finite dimensional linear operators,
  are encapsulated in the PETSc
  [`Mat`](https://www.mcs.anl.gov/petsc/petsc-current/docs/manualpages/Mat/index.html)
  object. The PETSc manual also has [a
  section](https://docs.petsc.org/en/latest/manual/mat/) on them.
  
  Some example usage is shown in the [commented code]({{< code-ref
  "parallel/live/Lec08.py" >}}).
  
## Lecturers

[Anne Reinarz](mailto:anne.k.reinarz@durham.ac.uk)

[Lawrence Mitchell](mailto:lawrence.mitchell@durham.ac.uk)


The course will be taught over both Term 1 and 2, and assessed by a
single piece of coursework due in Term 3.

Lecture slots are at 9am on Wednesday mornings. These will be run over
Zoom (you will need to be logged in with your Durham credentials)

https://durhamuniversity.zoom.us/j/96513562625?pwd=ZGxySUhwc0hPOEV1YW1TT0sxM3lWUT09

Meeting ID: 965 1356 2625
Passcode: 506890

A calendar subscription is available from
[https://tinyurl.com/comp4187-ics](https://tinyurl.com/comp4187-ics).

## Reading

Recommended:

LeVeque, Finite Difference Methods for Ordinary and Partial Differential Equations, SIAM (2007).

Optional:

Iserles, A first course in the numerical analysis of differential equations, Cambridge Texts in Applied Mathematics (2009).
