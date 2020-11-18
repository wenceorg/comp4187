---
title: "Coarse Grid Operator"
weight: 2
katex: true
---

# Constructing a coarse grid operator

We consider the discrete Poisson system with Dirichlet boundary conditions and 7 grid points,
$$\frac{-u_{i-1} + 2 u_i - u_{i+1}}{h^2}  =  f_i,  i=1\dots 5$$
$$u_0 = u_6 & = & 1, & \text{(inhomogeneous)}$$
where the mesh size is $h:=\frac{1}{6}$.

1. Formulate the system of equations in matrix form, i.e. $A_h u = b_h$. Take care with the boundary conditions.
2. Define a linear mapping $R: \mathbb{R}^5 \rightarrow \mathbb{R}^2$ according to the full weighting scheme. Set up the respective matrix $R$.
3. Define a linear mapping $P: \mathbb{R}^2 \rightarrow \mathbb{R}^5$ which prolongates a solution vector from the coarse to the fine grid using linear interpolation. Set up the respective matrix $P$.
How are $R$ and $P$ related?
4. Based on the matrices $R$, $P$ and $A_h$, compute the coarse grid operator $A_{2h}:=RA_h P$. Compare $A_{2h}$ to the operator
that you obtain by discretising the problem on the coarse grid. What do you observe?
5. What happens if you restrict a constant vector, e.g. $r = \vec{1}$. Can you ``mend'' the restriction operator
such that a constant vector is invariant under restriction? Does it matter?
6. Say you are given routines for interpolation, restriction, and applying the fine grid operator. How could you compute $RA_h P$?
