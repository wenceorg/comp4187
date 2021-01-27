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
