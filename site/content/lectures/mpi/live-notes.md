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
