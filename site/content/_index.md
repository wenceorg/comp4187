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

## Time and Place

In term 2 the course will run on Wednesdays at 12pm in CM107. Links to
live code, the recording, a small amount of commentary, and the
blackboard notes appear [in the notes section]({{< ref "live-notes.md"
>}}) after the fact.

{{< hint warning >}}

In the first week of term 2 (week beginning 10th January 2022), the lecture
is **online only**

{{< /hint >}}

{{< hint info >}}

You can attend remotely over
[zoom](https://durhamuniversity.zoom.us/j/97852350575?pwd=V0E5VHgxVkVuOFBOVk5POW5JY1Q0QT09),
and will need to be authenticated with your Durham account,

Meeting ID: 978 5235 0575  
Passcode: 646264

{{< /hint >}}

In term 1 lectures take place at 12:00 on Wednesdays in CM107.
Recordings of each lecture will be uploaded on encore, 
but you are encouraged to attend synchronously in person or via zoom.


## Syllabus

### Numerical Methods (Term 1)

- Topic 1: Spatial discretisation. Finite difference methods for partial differential equations (PDEs), stability, convergence, and consistency;
- Topic 2: Time dependent PDEs. Stability constraints for time-dependent PDEs, connection to eigenvalue analysis;
- Topic 3: Implicit ordinary differential equation (ODE) methods, and matrix representations of PDE operators;
- Topic 4: Advanced algorithms for PDEs. Fast methods of solving PDEs, high order discretisation schemes.

### Parallel Computing (Term 2)

- Distributed memory programming models: [MPI](https://www.mpi-forum.org).

- Parallel algorithms and data structures for finite difference codes.

- Measurement and modelling. Analysis of achieved performance,
  performance models, including the Roofline model.
  
- Use of the [PETSc](https://petsc.org) library for parallel computing.

- Irregular data distribution and load-balancing.


### Discussion forum

We have set up a [discussion forum]({{< repo >}}/discussions) where you
can ask, and answer, questions. You'll need a
[GitHub](https://github.com) account to use it, but you've all got one
of those already, right? Note that this repository and forum is
publically visible.

### Office hours
We're happy to answer any questions in office hours, email to arrange a time.

## Lecturers

- [Anne Reinarz](mailto:anne.k.reinarz@durham.ac.uk) (Term 1)
- [Lawrence Mitchell](mailto:lawrence.mitchell@durham.ac.uk) (Term 2)

## Reading

Recommended:

LeVeque, Finite Difference Methods for Ordinary and Partial Differential Equations, SIAM (2007).

Optional:

Iserles, A first course in the numerical analysis of differential equations, Cambridge Texts in Applied Mathematics (2009).
