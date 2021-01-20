---
title: Introduction
draft: false
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

### Lecture scribblings and video links

I'll add the annotated scribblings, live code examples, and links to
the videos (accessible with a Durham account) here.

- 2021-01-13: [Scribbles]({{< static-ref "parallel/2020-21/lec01.pdf"
  >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=fe338448-89f7-49b6-be1b-acaf00a72ad7),
  [code]({{< code-ref "parallel/live/hello.py" >}})
- 2021-01-20: [Scribbles(]{{< static-ref "parallel/2020-21/lec02.pdf"
  >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=ef0fb74d-cd43-4670-93be-acb600a5e14d)
  
  Some more detail on parallel scaling laws can be [found
  here](https://teaching.wence.uk/phys52015/notes/theory/scaling-laws/).
  For details on machine (or algorithmic) scaling, and its application
  to PDE solvers, I like [_A performance spectrum for parallel
  computational frameworks that solve
  PDEs_](https://arxiv.org/pdf/1705.03625) (the published paper is [in
  CCPE](https://onlinelibrary.wiley.com/doi/abs/10.1002/cpe.4401)).

## Lecturers

[Anne Reinarz](mailto:anne.k.reinarz@durham.ac.uk)

[Lawrence Mitchell](mailto:lawrence.mitchell@durham.ac.uk)


The course will be taught over both Term 1 and 2, and assessed by a single piece of coursework due in Term 3.

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
