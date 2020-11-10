---
title: "Two-Grid Iteration"
weight: 2
katex: true
---

# Fourier Analysis for Two-Grid Iteration
In this exercise we want to apply what we have seen already in the lectures on smoothers to the more complicated multigrid setting. For simplicity we restrict ourselves to 1D and two levels.

We stick to the Poisson example used in the smoother example:
$$\begin{array}{r c l}
-\cfrac{d^2 u}{d x^2}&=&f(x),~~~x\in(0,1),\vspace*{3mm}\\
u(0)=u(1) & = & 0.
\end{array}$$

This time, however, we want to consider the more general case of having $N+1$ grid points, where $N:=2K$, and a resulting mesh size $h:=1/N$.
A step towards multigrid methods consists in the  two-grid method based on coarse-grid correction.
In this particular case, we formulate the algorithm as follows:

1. After some iteration steps using a smoother (like Jacobi), compute residual $r^{old}:= b^h-A_h u^h$. The residual and the error $e^{old}$ fulfill the residual equation $r^{old}=A e^{old}$.
2. Restrict the residual to the coarse grid using an operator $R$. This yields a (residual-like) vector $r^{2h}$ on the coarse grid. The coarse grid is assumed to have $K+1$ points.
3.  Solve the residual equation $A_{2h} e^{2h} = r^{2h}$ on the coarse grid. $A_{2h}$ corresponds to the coarse-grained system that resembles $A_h$ on the fine grid.
4. Interpolate the resulting coarse-grid approximation of the error $e^{2h}$ to the fine grid and correct the fine-grid error $e^{new}:=e^{old}-Pe^{2h}$. The interpolation operator shall be denoted by $P$.

Furthermore, we define vectors $q_h^m$ with components $(q_{h}^m)_i:=\sin(m\pi h i)$. With respect to the fine grid, we have a low frequency if $m<N/2$, and a high frequency if $m\geq N/2$.\newline
In the following, we want to step through the Fourier analysis for this method and investigate the convergence behaviour, considering one cycle of this two-grid algorithm.

1. Give a closed expression for $e^{new}$ which only depends on $e^{old}$ and not on $e^{2h}$ anymore. You may use the operators $R$, $P$, $A_{2h}$ and $A_h$ from above.
2. Define the restriction operator $R$ by injection. Show that the restriction of any error frequency $R q_h^m$ yields a low frequency, that is
$$ R q_h^m = \left\{\begin{array}{r c l}
q_{2h}^m & \hbox{if} & m<N/2\vspace*{3mm}\\
-q_{2h}^{N-m} & \hbox{if} & m\geq N/2.\end{array}\right.$$

3. For interpolation, we want to use the linear interpolation scheme:
$$(P q^m_{2h})_i = \left\{ \begin{array}{lll}
      \underbrace{(q^m_{2h})_{i/2}}_{\mbox{$=(q^m_h)_i$}} & \mbox{ for } & i=2,4,\ldots,N-2 \\
      && \\
    \frac{1}{2} \bigl( \underbrace{(q^m_{2h})_{(i-1)/2}}_{\mbox{$=(q^m_h)_{i-1}$}} +
                                \underbrace{(q^m_{2h})_{(i+1)/2}}_{\mbox{$=(q^m_h)_{i+1}$}} \bigr)
                                 &  \mbox{ for } & i=1,3,\ldots,N-1. \end{array} \right.$$
Use the function definitions
$$\begin{array}{ r c l}
\frac{1}{2} (\cos(\pi i)+1) & = & \left\{ \begin{array}{rl}
 1 & \mbox{ for } i=2,4,\ldots,N-2 \\
 0 & \mbox{ for } i=1,3,\ldots,N-1 
\end{array} \right.\vspace*{3mm} \\
\frac{1}{2} (-\cos(\pi i)+1) & = & \left\{ \begin{array}{rl}
 0 & \mbox{ for } i=2,4,\ldots,N-2 \\
 1 & \mbox{ for } i=1,3,\ldots,N-1 
\end{array} \right. \end{array}$$ 
and
$$(q^{N-m}_h)_i=\sin((N-m) \pi h i)  =  \underbrace{\sin(N \pi h i)}_{=0}
                                \cos(m \pi h i) - \cos(N \pi h i) \underbrace{ \sin(m \pi h i) }_{= (q^m_h)_i } = -\cos(\pi i)(q^m_h)_i$$
to re-write the interpolated coarse grid frequency $P q_{2h}^m$ as
$$ P q_{2h}^m = a_m\cdot q_h^m + b_m\cdot q_h^{N-m}$$
with (frequency-dependent) constants $a_m, b_m$. What does the latter equation tell us about the frequency of the interpolated function $P q_{2h}^m$?
4. Putting the results from prolongation and restriction together, we can derive by further computation (not discussed in the exercise) that
$$ PA_{2h}^{-1}RA_hq_h^m=\left\{ \begin{array}{lll}
                               q^m_h 
                                -\frac{(1-\cos(m \pi h))^2}{\sin(m \pi h)^2} q^{N-m}_h & 
                               \mbox{ if } & m < \frac{N}{2} \\[0.5ex]
                               -\frac{(1-\cos(m \pi h))^2}{\sin(m \pi h)^2} q^{N-m}_h +
                               q^m_h 
                               & \mbox{ if } & m \ge \frac{N}{2} \end{array} \right. \\
  = q^m_h - \frac{(1-\cos(m \pi h))^2}{\sin(m \pi h)^2} q^{N-m}_h$$
Assume that the initial error is a linear combination of two sines: $e^{old} = x_1q_h^m + x_2q_h^{N-m}$ with $m<N/2$. Express $PA_{2h}^{-1}RA_he^{old}$ in terms of $q_h^m$ and $q_h^{N-m}$,
a $2\times 2$-matrix $B_m$, and the vector $(x_1,x_2)^T$. That is, find a representation
$$PA_{2h}^{-1}RA_he^{old} = \begin{pmatrix}
 q_h^m & q_h^{N-m}
\end{pmatrix}
B_m
\begin{pmatrix}
 x_1 \\ x_2
\end{pmatrix}.$$
With this in mind, we can simplify the analysis with a change of basis. Let
$$ Q = (q_h^1, q_h^{N-1}, q_h^2, q_h^{N-2}, \dots, q_h^{K-1}, q_h^{N-K+1}, q_h^{K}).$$
As this matrix is invertible, we can find a vector $x^{new}$ with $e^{new} = Qx^{new}$ and a vector $x^{old}$ with $e^{old} = Qx^{old}$.
The entry $(x^{old})_i$ can be interpreted as the weight of the frequency in the i-th column of $Q$.
If we left-multiply $e^{new}$ with $Q^{-1}$ we have
$$ x^{new} = Q^{-1}e^{new} = Q^{-1}e^{old} - Q^{-1}PA_{2h}^{-1}RA_he^{old} = x^{old} - C x^{old} = (I - C) x^{old}.$$
That is, we have found a frequency mapping $x \mapsto (I-C)x$ and may directly work with the error's frequency components instead with the error itself.

Determine the matrix $C$. ($C$ will be block diagonal and consist of blocks $B_m$.)

4. In order to remove high frequency errors, we apply two Jacobi iterations before ({\textit pre-smoothing}) and after ({\textit post-smoothing}) the coarse-grid correction scheme.
Following the Fourier analysis from the finite-difference exercise for the basis vectors $(q_h^m)_{m=1,\dots,N-1}$, one weighted Jacobi iteration ($\omega=1/2$) corresponds to the update rule
(again working on the error's frequency components with the same ordering as in 3.
$$
x \mapsto M_f x.
$$
I.e. for the frequency pair $m$ and $N-m$ we obtain
\begin{displaymath}
\left(\begin{array}{c}
x_1\\
x_2\end{array}\right) \rightarrow \left(\begin{array}{c c}
\frac{1}{2}\left(1+\cos(m\pi h)\right) & 0\\
0 & \frac{1}{2}\left(1-\cos(m\pi h)\right)
\end{array}\right)
\left(\begin{array}{c}
x_1\\
x_2\end{array}\right)
\end{displaymath}

Because $C$ is a block diagonal matrix and $M_f$ is diagonal, we may limit the discussion to frequency pairs. The general results then follow easily.

Give an estimate for the maximum eigenvalue of the overall solver operations, that is pre-smoothing $\rightarrow$ restriction $\rightarrow$ coarse-grid correction $\rightarrow$ interpolation $\rightarrow $post-smoothing.



