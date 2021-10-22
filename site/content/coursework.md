---
title: "Coursework 1: Euler-Bernoulli Beam Theory"
weight: 3
katex: true
---

# A 1D Euler-Bernoulii Beam

{{< hint warning >}}

The submission deadline for this work is November 4th.

This coursework is worth 20% of the total mark for the module.

See [below]({{< ref "#submission" >}}) for submission details.

{{< /hint >}}


## Introduction

In this coursework, we're going to implement an Euler-Bernoulli beam in 1D. [Euler–Bernoulli beam theory](https://en.wikipedia.org/wiki/Euler–Bernoulli_beam_theory), sometimes known as classical beam theory, is a
model for calculating the load-bearing behaviour of a beam.. It is essentially just a simplification of elasticity theory and covers only small deflections 
under lateral loading. It is considered one of the corner-stones of structural engineering. From our less engineering-focused perspective it is a
time-dependent 4th order differential equation that we can approximate with finite differences.

{{< manfig src="Beam.jpg" width="50%" >}}


## The write-up
In addition to the implementation of the finite difference scheme and explicit Euler solver you should provide detailed answers
to the questions in each section. For the theoretical questions this includes your reasoning.

For the questions about your solver this means performing a relevant numerical experiment,
noting down the results and drawing conclusions from the data. The results should be plotted in a relevant manner and the data
going into the plot should additionally be provided as a table.

The complete write-up should not exceed a page.

You may want to place both the implementation and your write-up into a jupyter-notebook.

## The solver

{{< hint info >}}
You should do your implementation for this part either in a stand-alone python file or in a jupyter-notebook. You may use numpy and pyplot.
Additional libraries can also be used as long as they do not implement any of the numerical methods, i.e. a different plotting tool, 
or an optimisation library can be imported, while a finite-difference toolbox can not.
{{< /hint >}}

Discretise the equation
$$
\partial_{tt} u(x,t) = -k \partial_{xxxx}u(x,t)
$$
with a small material parameter $k$ on the unit interval $[0, 1]$ using a finite-difference methdod.
As boundary conditions we will keep both ends of the beam fixed at zero displacement:
$$
u(0,t)=u(1,t)=0
$$
and (since this is a fourth-order equation), we need to also set the bending moment of the beam
$$
\partial_{xx}u(0,t) = \partial_{xx}u(1,t) = 0.
$$
We also need to set some initial conditions
$$
u(x,t=0) = \sin(\pi x)+\frac{1}{2}\sin(3\pi x),~
\partial_t u(x,t=0) = 0.
$$

The analytical solution to this problem can be computed directly:
$$
u*(x,t) = \cos(\pi^2 \sqrt{k} t)\sin(\pi x) + \frac{1}{2} \cos(9\pi^2 \sqrt{k} t)\sin(3\pi x).
$$
You may use the analytical solution to test your implementation and to compute errors.


{{< hint info >}}
You may start by modifying code shown in the lecture.
{{< /hint >}}

{{< question "Questions" >}}
1. Derive a centred differences stencil for the spatial component of the problem.
1. The second-order in time equation can easily be transformed into a coupled system of first-order in time equations. Derive the first-order system and apply an explicit Euler time-stepping scheme.
1. Implement the time-stepping scheme and stencil to find a numerical approximation to $u*$. Use a small value for the end time and for $k$, e.g. $k=0.01$.
1. Is there a time-step size limitation needed to ensure stability? If so what is it?
1. What convergence order do you observe? Is this what you expected? Why/why not?
{{< /question >}}

## Submission and mark scheme {#submission}

The work will be marked on the basis of two things

1. Your submitted code;
2. A write-up discussing answers to the questions and your
   findings.

You should develop your code and writeup in the GitHub classroom repository for this assignment.
Remember to commit regularly. In addition to the code and writeup, your repository should contain a
short `README` file that describes which artifacts we should look at for marking.

You should submit to ULTRA a single text file `$USERNAME.txt` containing the commit hash of the code
and writeup you want us to mark.

### Mark scheme

Code: 25%
Writeup: 75%
