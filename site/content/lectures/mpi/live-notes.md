---
title: "Term 2: live lecture notes"
draft: false
weight: 100
katex: true
---

# Lecture slides 2021/22 edition

Slides as produced during the live lectures. Recordings of the live
sessions are available if you're appropriately logged in. If you think
you should have access but don't, please [get in
touch](mailto:lawrence.mitchell@durham.ac.uk).

- 2022-01-12: [Notes]({{< static-ref "parallel/2021-22/lec01.pdf"
  >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=a2578ab5-e2b9-4a41-ab71-ae1b00d784b0),
  [code]({{< code-ref "parallel/live/2021-22/lec01.py" >}}).
  
  Have a go at the [hello world]({{< ref "hello.md" >}}) exercise
  which walks through setting up an environment with MPI installed.

- 2022-01-19: [Notes]({{< static-ref "parallel/2021-22/lec02.pdf" >}}), [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=4ed36e00-5ef0-42dd-83c2-ae2100946181).

  We had a bit of a palaver with the network being terrible, so sorry
  to those attending online for the drop out in the second half.
  Fortunately the encore recording got everything, so we've got a
  complete record [the very last bit of the lecture got cut off, but I
  went through this a bit fast anyway so will recap next time].
  
  I got confused writing the speedup for strong and weak scaling (and
  didn't really define efficiency). I've fixed my todo note and added
  a few more details in the uploaded notes.

  From next week we are in **E245**.

- 2022-01-26: [Notes]({{< static-ref "parallel/2021-22/lec03.pdf"
  >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=0e3fe682-0bc2-4920-8fa6-ae2900dee766),
  [code]({{< code-ref "parallel/live/2021-22/lec03.py" >}})
  
  We went over scaling behaviour a bit more and wrote some simple
  ping-pong code (linked above). A more fleshed-out version of this
  (with more comments and argument parsing) is available as
  [`pingpong.py`]({{< code-ref "parallel/live/pingpong.py" >}}). Have
  a go at running this (on your own machine and/or Hamilton), the
  [pingpong exercise]({{< ref "pingpong.md" >}}) has more details on
  what we're looking for.

- 2022-02-03: [Notes]({{< static-ref "parallel/2021-22/lec04.pdf"
  >}}), [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=adb7447d-11dc-4664-8c86-ae3000d794a0), [plotting code]({{< code-ref
  "parallel/live/2021-22/ping-pong-plots.py" >}})
  
  We started out looking at results from running the ping-pong
  benchmark run on both old (Hamilton 7) and new ([Hamilton
  8](https://www.dur.ac.uk/arc/hamilton/migration/)) hardware. You
  should be able to back out the network latency and bandwidth by
  fitting the model $t(b) = \alpha + \beta b$ to the data. We noted
  that the pickle protocol has much higher latency.
  
  Then I talked about domain-decomposing finite difference grids, and
  why parallel computing works at all (because there is sparsity in
  the computation).
  
  Next time, if there is time (I need to do some planning), I would
  like to look at the analysis of scaling limits for
  Jacobi iteration from [_Scaling Limits for
  PDE-based
  simulation_](http://www.mcs.anl.gov/papers/P5347-0515.pdf), so

  {{< exercise >}}
  Please read the introduction and up to the end of Section II.B.1
  (Jacobi iteration) from that paper, we'll try and discuss the key
  points.
  {{< /exercise >}}

- 2022-02-09: [Annotated paper]({{< static-ref
  "parallel/2021-22/Fischer2015.pdf" >}})
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=56478af1-c709-4cbe-9d87-ae3700d56272),
  
  
  Live notes only contain administrative information, reproduced here.
  The second coursework should go live in the next short while. It
  will be using [PETSc](https://petsc.org/) via
  [petsc4py](https://pypi.org/project/petsc4py/) for parallel data
  structures so for most of the remaining slots I will focus on live
  code demonstrating the ideas and usage (which is somewhat
  non-trivial). You'll want to have PETSc installed on whatever you're
  using for development, so please follow their instructions and get
  in touch if you can't manage things.
  
  Some administrative matters:
  
  - No lecture next week on 2022-02-16 due to [UCU strike
    action](https://www.ucu.org.uk/article/11896/Why-were-taking-action).
    
  - No lecture (subject to strikes being cancelled) on 2022-03-02 due
    to more strike action.
    
  - I need to either arrange to deliver the lecture on 2022-03-09
    remotely, or else reschedule for another time (since I will be in
    [Dagstuhl](https://dagstuhl.de) that week).

- 2022-02-23: [Code]({{< code-ref "parallel/live/2021-22/lec06.py" >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=365190be-a98b-45cd-8e11-ae4500d750f9)
  
  We started looking at [PETSc](https://petsc.org/) for parallel data
  structures. The [second coursework]({{< ref "coursework2.md" >}}) is
  now live and uses PETSc extensively. So please do try and get an
  install working so that we can debug issues quickly.
  
  I introduced the PETSc object model, and manipulation of Vectors. I
  recommend also skimming the PETSc manual (particularly the
  [introduction](https://petsc.org/release/docs/manual/getting_started/)).
  
  More administrative matters:
  
  - No lecture next week on 2022-03-02 due to continuing strike
    action.

  - The lecture on 2022-03-09 will be **remote only** (I will send
    email reminding everyone).

- 2022-03-09: [Notes]({{< static-ref "parallel/2021-22/lec09.pdf" >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=f7125450-3852-43e7-b31b-ae5300d72eea),
  [code]({{< code-ref "parallel/live/2021-22/lec09.py" >}})
  
  Apologies for the delayed upload this week. Mostly what we covered
  this week was the basics of using PETSc's
  [DMDA](https://petsc.org/release/docs/manualpages/DMDA/DMDA.html#DMDA)
  objects for managing structured grids. These manage the tedious
  detail of constructing communication patterns for ghost exchange and
  insertion into distributed sparse matrices. We will use these in our
  implementation of multigrid in the [second coursework]({{< ref
  "coursework2.md" >}}).
  
  Mostly we looked at creating
  [`Vec`s](https://petsc.org/release/docs/manual/vec/#dm-local-global-vectors-and-ghost-updates)
  and [`Mat`s](https://petsc.org/release/docs/manual/mat/) from these
  [`DMDA`](https://petsc.org/release/docs/manualpages/DMDA/DMDA.html#DMDA)
  objects. The reason to do this is that the vectors and matrices now
  remember that they came from the DMDA and so this enables certain
  extra methods (particularly for insertion into matrices which we
  will see next time). Particularly, the DMDA also knows how to refine
  itself and construct grid transfer operators between the two grids
  (very useful for multigrid methods).
  
  Next time we will glue everything together.

- 2022-03-16: [Code]({{< code-ref "parallel/live/2021-22/lec10.py" >}}),
  [video](https://durham.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=4ed89385-62cd-4209-b22d-ae5a00d7900b)
  
  We finished up for the year by looking at how to discretise a
  constant coefficient Laplacian in parallel using DMDA. The core idea
  is that we need to map between global, local, and ghosted indices.
  
  We also discussed appropriate scaling of the entries in the operator
  to work with PETSc's builtin prolongation and restriction matrices.
  Effectively this means we scale the equations we're solving by the
  volume element for our grid (how big is a single cell?), and put
  "compatible" things in the boundary rows.
  
  If you want to play around with the PETSc C example I showed towards
  the end, it is
  [`ex45`](https://petsc.org/main/src/ksp/ksp/tutorials/ex45.c.html).
  If you have a PETSc install, then the code lives in
  `$PETSC_DIR/src/ksp/ksp/tutorials/ex45.c`, with `PETSC_DIR` and
  `PETSC_ARCH` set appropriately, `make ex45` in that directory will
  build it. This example implements (in C) the constant coefficient
  Laplacian in 3D using DMDA, so it is somewhat similar to the
  equation in the coursework (although you will need a different
  stencil).
  
  That's all for this term, for queries on the course, the best place
  is the [discussions forum]({{< repo >}}/discussions). Good luck for
  the summer!
