---
title: "Coursework 2: multigrid solvers"
weight: 4
katex: true
---
# A 3D multigrid solver

{{< hint warning >}}

The submission deadline for this work is 5th May 2022 at 2pm.

You can accept the assignment on [github classroom](https://classroom.github.com/a/aS5kAaVW)

See [below]({{< ref "#submission" >}}) for submission details.

{{< /hint >}}

## Introduction

In this coursework, we're going to implement a parallel multigrid
solver initially in one dimension for the Euler-Bernoulli beam
and finally in three dimensions for the variable-coefficient Laplacian.

We are using [PETSc](https://www.mcs.anl.gov/petsc/), via
[petsc4py](https://pypi.org/project/petsc4py/), to provide the
parallel data structures.

There's a skeleton Python package that provides a lot of the
infrastructure that you will build on to develop your solver.

To get going, you'll need to install `petsc4py` in your virtual
environment. On your own machine, `pip install petsc4py` should be
sufficient. This will go away and build PETSc, followed by `petsc4py`.
If you're using conda, you can install `petsc4py` in your conda
environment with `conda install -c conda-forge petsc4py`.

{{< details "PETSc on Hamilton 8" >}}
{{< hint info >}}
You will need to build PETSc and petsc4py on Hamilton 8 (for parallel
runs).

Load the following modules:

```
gcc
intelmpi
openblas
python
```

and create a virtual environment:

```
$ python3.9 -m venv pscii
```

Activate the virtual environment and install dependencies
```
$ pip install mpi4py numpy
```

Download PETSc (I recommend you do this in the large "data" directory)
```
$ cd /nobackup/$USER
$ git clone https://gitlab.com/petsc/petsc.git
$ cd petsc
$ ./configure --with-debugging=0 --with-openblas-dir=$OPENBLAS_HOME
$ make PETSC_DIR=/nobackup/$USER/petsc PETSC_ARCH=arch-linux-c-opt all
$ make PETSC_DIR=/nobackup/$USER/petsc PETSC_ARCH=arch-linux-c-opt check
```

If anything fails at this point **get in touch**.

Now install petsc4py (still with the virtual environment activated)
```
$ export PETSC_DIR=/nobackup/$USER/petsc
$ export PETSC_ARCH=arch-linux-c-opt
$ pip install $PETSC_DIR/src/binding/petsc4py/
```

petsc4py should now be usable having activated your virtual
environment. Don't get to load the relevant modules every time.
{{< /hint >}}
{{< /details >}}

{{< hint warning >}}

Building PETSc is sometimes problematic. If the installation
fails for any reason **GET IN TOUCH** and we'll figure it out. The
best way to do this is via the [discussion forum]({{< repo
>}}/discussions).

{{< /hint >}}

## Getting and installing the `mgsolver` package

We will use [GitHub classroom](https://classroom.github.com) to manage
the submissions. To set up and fork the template repository, follow
[this link](https://classroom.github.com/a/aS5kAaVW).

You should work in your fork and push your code regularly. Having
forked the repository, you can clone it locally and install the
package. I recommend using an _editable install_ since you'll be
developing new code in the package.

```
$ git clone git@github.com:Durham-COMP4187/your-repo-name-here.git comp4187-coursework
$ pip install -e comp4187-coursework/
```

After doing this, you should be able to run the tests with (they will
all fail)

```
$ pytest tests
```
{{< hint warning >}}
If you can't get this far for whatever reason, **GET IN TOUCH**.
{{< /hint >}}
## Package layout

The `mgsolver` package contains a number of classes, some of which are
missing functionality that you are to implement. The main classes that
we need are

- `grid.Grid3D` and `grid.GridHierarchy`. These provide a coarse grid
  and a hierarchy of regularly refined grids. We'll just need to
  construct these.
- `mgsolver.MGSolver`: This class manages the multigrid solver. It has
  unimplemented methods for Jacobi iteration (`jacobi`), a V-cycle
  (`vcycle`), and a W-cycle (`wcycle`), which you will need to
  implement.
- `operator.AbstractOperator`: You should produce a subclass of this
  for your operators and implement the requisite abstract methods.

  1. `mult` do a matrix-vector multiply.
  2. `diagonal` a property that returns the diagonal of the operator.
  3. `as_sparse_matrix` return the operator as a sparse matrix.

Additionally, visualisation output of solution vectors to
[VTK](https://vtk.org) files viewable in
[Paraview](https://www.paraview.org) can be produced using the
`write_output` function.

Here is a sketch of how you would use the package (eliding details of
the implementation of the operator's methods).

```python
from functools import cached_property
from mgsolver import AbstractOperator, Grid3D, GridHierarchy, MGSolver, PETSc
from mpi4py import MPI


# Define the operator we want to apply
# Must inherit from AbstractOperator
class Poisson7pt(AbstractOperator):
    def __init__(self, grid):
        # Can do some stuff here, but remember to always do
        super().__init__(grid)

    # We need to implement this property. A @cached_property is like
    # a @property, but only gets evaluated once.
    @cached_property
    def diagonal(self):
        pass

    # We need to implement this method
    def mult(self, x, y):
        # x is the input vector, y is the output vector.
        pass

    # Finally, we need to implement this method
    def as_sparse_matrix(self):
        # Return the operator as a sparse matrix
        pass


# Create a coarse grid with 4 vertices in each direction
coarse_grid = Grid3D(4, 4, 4, comm=MPI.COMM_WORLD)
# Create a hierarchy with two refinements (3 levels in total)
hierarchy = GridHierarchy(coarse_grid, nrefinements=2)
# You can index the GridHierarchy like a normal list.
fine_grid = hierarchy[-1]
# Now we can build a solver
solver = MGSolver(hierarchy, Poisson7pt)

# Create vectors to hold the solution and right hand side
x = fine_grid.createGlobalVector()
b = fine_grid.createGlobalVector()

# To get an operator on a given level
A_fine = solver.get_operator(len(hierarchy)-1)
# The solver also provides storage for vectors of residuals and so
# forth on each level. The jacobi iteration needs somewhere to store
# the residual.
r = solver.residuals[len(hierarchy)-1]
# To run 10 iterations of Jacobi
solver.jacobi(A, x, b, r, niter=10)
# To solve using a V-cycle using 1 iteration of pre- and post-smoothing
# to a relative tolerance of 1e-5
solver.solve(x, b, rtol=1e-5, presmooth=1, postsmooth=1,
             cycle_type=solver.Type.V)
# To solve using a W-cycle using 1 iteration of pre-smoothing and 2
# iterations of post-smoothing to a relative tolerance of 1e-8
solver.solve(x, b, rtol=1e-8, presmooth=1, postsmooth=2,
             cycle_type=solver.Type.W)
```

For a complete example, see the tests in `tests/test_one_dim.py`,
which implement a one-dimensional example.

The tests themselves do not pass, since the various bits of the `MGSolver`
class are not completed. You can run the tests with
[`pytest`](https://pytest.org), using `pytest tests`. After
successfully implementing the Jacobi iteration and V-cycle, the test
run looks something like
```
$ pytest tests/test_one_dim.py -v
================================== test session starts ===================================
platform darwin -- Python 3.8.6, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- pscii/bin/python3
cachedir: .pytest_cache
rootdir: XXX, configfile: setup.cfg
collected 3 items

tests/test_one_dim.py::test_mms_convergence PASSED                                 [ 33%]
tests/test_one_dim.py::test_two_grid[Jacobi coarse grid] PASSED                    [ 66%]
tests/test_one_dim.py::test_two_grid[Exact coarse grid] PASSED                     [100%]

=================================== 3 passed in 0.34s ====================================
```

You can also run the tests in parallel by doing
```
$ mpiexec -n 4 tests/test_one_dim.py -v
```

## Part 1: Reimplementing the beam

In the previous coursework you implemented a 5-point stencil for the Euler-Bernoulli beam
We will solve the stationary variant of this equation (i.e. no time-component this time).
In particular, we will solve a three-point bending test. The beam is supported at both ends,
and at the centre a concentrated load is applied.

$$
\delta(x-\frac{1}{2}) = -k \partial_{xxxx}u(x)
$$
with a small material parameter $k$. Here $\delta$ is a Dirac function, it is one at the centre
of the beam $x=\frac{1}{2}$ and zero everywhere else.

Boundary conditions remain as before:
u(0,t)=u(1,t)=0
$$
and
$$
\partial_{xx}u(0,t) = \partial_{xx}u(1,t) = 0.
$$


To implement this create a class `Bernoulli5pt` that discretises the
spatial operator using a 2nd order accurate 5-point stencil. Watch out
for the boundary conditions.

{{< hint info >}}
Hint: Have a look at `tests/test_one_dim.py`
{{< /hint >}}

{{< hint info >}}
You should do your implementation for this part in a file called
`part1_euler_bernoulli.py` placed in the root of the repository.
{{< /hint >}}


The analytical solution is
$$w(x) = \begin{cases}
    \frac{x(4x^2-3)}{48k}, & \mbox{for } 0 < x < \frac{1}{2} \\
    \frac{(x-1)(1-8x+4x^2)}{48k}, & \mbox{for } \frac{1}{2} < x < 1
    \end{cases}$$
    
For now we will solve the resulting linear system with a direct solver.
You can use one of the built-in PETSc solvers for this. Later we will
implement a multigrid solver. At that stage you may want to go back to
this equation to see how multigrid performs.

{{< question "Part 1a questions" >}}
1. How does the error in your numerical solution behave under grid
   refinement? Can you explain what you see?
{{< /question >}}




## Part 2: The 3D Darcy Equation


Discretise the equation
$$
\partial_t u - \nabla \cdot K(x, y, z) \nabla u = f(x, y, z)
$$
on the cubic domain $\Omega = [0, 1] \times [0, 1] \times [0, 1]$,
using forward Euler as a timestepping scheme. After some time-stepping
the equation will reach its steady-state, which is to say that the time
derivative will become zero. Compare solving the stationary state-state
equation 
$$
- \nabla \cdot K(x, y, z) \nabla u = f(x, y, z)
$$
directly using a linear solver with time-stepping towards the steady-state.

To do this, create a class `Poisson7pt` that discretises the spatial
operator using a 2nd order accurate 7-point stencil (as derived in lectures).
$$
-\nabla \cdot K(x, y, z) \nabla u.
$$

Using
$$
K(x, y, z) = cos(\pi y)
$$
$$
f(x, y, z) =  (\pi+3\pi^2) \sin(\pi x)\sin(\pi y)\sin(\pi z),
$$
Dirichlet boundary conditions on the boundary
$$
u(x, y, z) = 0.
$$
The exact solution for this
problem is
$$
u^*(x, y, z) = \sin(\pi x)\sin(\pi y)\sin(\pi z).
$$


### Part 2a: timestepping
{{< hint info >}}
You should do your implementation for this part in a file called
`part2_explicit_euler.py` placed in the root of the repository.
{{< /hint >}}

Implement an explicit Euler time-stepping scheme using your 7-point stencil.

{{< hint info >}}
Ensure that your implementation works correctly in parallel as well as
serial (when run with MPI).
{{< /hint >}}

{{< question "Part 2a questions" >}}
1. How does the error in your numerical solution behave under grid
   refinement? Can you explain what you see?
2. Is the same solution reached by solving the stationary equation 
   and by solving the time-dependent problem after reaching the steady-state?
   How does the error behave with respect to time to solution in these two cases?
{{< /question >}}

### Part 2b: A higher-order scheme

{{< hint info >}}
This part doesn't need to you to write any code.
{{< /hint >}}

{{< question "Part 2b questions" >}}

1. Derive, but do not implement, the 4th order accurate stencil for a
   5-point discretisation of the Laplace operator in one dimension.
1. How do you have to modify the stencil at the boundary to maintain the
   accuracy for:
    1. Dirichlet conditions $u = g$?
    1. Neumann conditions $\nabla u \cdot n = h$?
1. Would this spatial discretisation have the same timestep restriction
   as the 2nd order operator, or a different one? Explain your answer.

{{< /question >}}

## Part 3: multigrid

### Part 3a: completing the multigrid solver
Implement the missing pieces in the `MGSolver` class, namely

- `MGSolver.jacobi`
- `MGSolver.vcycle`
- `MGSolver.wcycle`

You should do this directly in the `mgsolver/mgsolver.py` file (don't
forget to commit it!). If you do this correctly, the one dimensional
tests should now pass. You can now test the multigrid solver on the
Euler-Bernoulli beam example you have implemented in part 1.

{{< hint info >}}
Ensure that your implementation is correct in both serial and
parallel. Up to round-off error, you should get the same results
independent of the number of processes.
{{< /hint >}}

{{< question "Part 3a questions" >}}
1. For the Euler-Bernoulli beam what mesh convergence do you get with the new
   multigrid solver? Does it differ from the behaviour using a direct solver?
   Do you have to adjust the tolerance to which you solve the problem as you add more
   grid levels?
{{< /question >}}

### Part 3b: solving for a steady state

{{< hint info >}}
You should do your implementation for this part in a file called
`part2_multigrid.py` placed in the root of the repository.
{{< /hint >}}

Using the same `Poisson7pt` operator that you implemented for Part
2a, we will now solve for the steady state directly (rather than
timestepping towards it).

Confirm that your implementation is correct by doing an MMS
convergence test. For large problems you will probably want to run in
parallel.

{{< hint info >}}
If your operator definition was correct in parallel in Part 2, you
should not have to worry very hard about parallelism in this part,
since everything is done with "collective" operations.
{{< /hint >}}

{{< question "Part 3b questions" >}}

1. What mesh convergence do you get for this problem? Do you have to
   adjust the tolerance to which you solve the problem as you add more
   grid levels?
1. For this problem, which method (jacobi, V-cycles, W-cycles) works
   best when you add more grid levels?

   Consider both algorithmic convergence and time to solution.
1. Play around with the number of smoothing steps, does that change
   your conclusions?

{{< details "Performance hint" >}}

You may wish to pull the body of the matrix-vector `mult` method out
and try JIT-compiling it with numba. I found that made a big
(positive) difference in the performance of my code.

{{< /details >}}

{{< /question >}}


## Submission and mark scheme {#submission}

The work will be marked on the basis of three things

1. Your submitted code;
2. A short report discussing answers to the questions and your
   findings;
3. A brief (10 min) oral exam with the lecturers. We will use this to
   have a brief discussion about your implementation choices and code,
   and any interesting things you found in your numerical experiments.
   No need to prepare anything specific.

You should submit to LearnUltra only the commit hash of the code on
   github you want us to mark.
   
After submission, please contact the lecturers to arrange a time for
the oral exam. Please do so within 5 days of the submission deadline.

### Mark scheme

- Part 1 [15 marks]
    - implementation [10 marks]
    - questions/writeup [5 marks]
- Part 2 [35 marks]
    - Part 2a [25 marks]
       - implementation [15 marks]
       - questions/writeup [10 marks]
    - Part 2b [10 marks]
- Part 3 [35 marks]
    - Part 3a [10 marks]
    - Part 3b [25 marks]
       - implementation [15 marks]
       - questions/writeup [10 marks]
- Code formatting (tested via flake8) [5 marks]
- Brief oral exam [10 marks]
