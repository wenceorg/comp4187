---
title: "Finite Differences"
weight: 2
katex: true
---

# Finite Differences
Consider the one-dimensional Poisson equation with homogeneous Dirichlet conditions
$$-\frac{d^2 u}{d x^2}=f(x),~~~x\in(0,1)$$
with Dirichlet boundary conditions
$$u(0)=u(1)  =  0.$$
1. Discretise the Poisson equation by finite differences using an equidistant mesh size $h=1/N$ and $N+1$ grid points.
2. Write the finite difference approximation from 1. in matrix-vector form $Au=b$. Therefore, define the entries of the matrix $A\in\mathbb{R}^{N+1\times N+1}$.
3. Write the finite difference approximation as $Au=b$, where $A\in\mathbb{R}^{N-1\times N-1}$ and $b\in\mathbb{R}^{N-1}$, by substituting the values for $u(0)$ and $u(1)$.


# Eigenvalues and eigenvectors
When analysing the properties of numerical algorithms it is often helpful to know about the spectrum (eigenvectors) of the operator being treated.
A non-zero vector $x$ is an eigenvector of a matrix $A$ if and only if there exists a scalar $\lambda$ such that
$$Ax=\lambda x.$$
The scalar $\lambda$ is the corresponding eigenvalue.

Show that the discretised sine, i.e. $u_i = sin(k\pi ih)$, is an eigenvector with eigenvalue $\lambda=(4/h^2)\sin^2(k\pi h/2)$ of the finite difference matrix $A$
in the previous exercise.

You may find the following trigonometric identities useful:
$$ \sin(a+b)+\sin(a-b) = 2\sin(a)\cos(b)$$
$$ \cos(2x) = 1-2\sin^2(x)$$
