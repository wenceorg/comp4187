---
title: "Coursework: a 3D multigrid solver"
weight: 3
katex: true
---
# A 3D multigrid solver

{{< hint warning >}}

The submission deadline for this work is 13th May 2021.

You should submit a single text file to DUO containing the git hash of
the repository commit you would like us to mark.

See below for submission details.

{{< /hint >}}

In this coursework, we're going to implement a parallel multigrid
solver in three dimensions for the variable-coefficient Laplacian.

We are using [PETSc](https://www.mcs.anl.gov/petsc/), via
[petsc4py](https://pypi.org/project/petsc4py/) to provide the parallel
data structures.

There's a skeleton Python package that provides a lot of the
infrastructure that you will build on to develop your solver.

To get going, you'll need to install `petsc4py` in your virtual
environment. On your own machine, `pip install petsc4py` should be
sufficient. This will go away and build PETSc, followed by `petsc4py`.

{{< hint info >}}

On Hamilton, I provide a useable version of PETSc.

To use it, you'll need to use the following modules
```
gcc/9.3.0
intelmpi/gcc/2019.6
```
and set the environment variables
```
export PETSC_DIR=/ddn/data/vtdb72/petsc
export PETSC_ARCH=arch-linux2-c-opt
```

After that you can `pip install petsc4py` in your virtual environment.

Don't forget to load those modules and export those environment
variables every time your log in.
{{< /hint >}}

{{< hint warning >}}

Building PETSc is sometimes problematic. If the `pip install` route
fails for any reason **GET IN TOUCH** and we'll figure it out. The
best way to do this is via the discussion forum.

{{< /hint >}}

## Getting and installing the `mgsolver` package

We will use [GitHub classroom](https://classroom.github.com) to manage
the submissions. To set up and fork the template repository, follow
[this link](https://classroom.github.com/a/YYCs7KMb).

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

Here is a sketch of how you would use the package

```python
from functools import cached_property
from mgsolver import AbstractOperator, Grid3D, GridHierarchy, MGSolver, PETSc
from mpi4py import MPI

# Create a coarse grid with 4 vertices in each direction
coarse_grid = Grid3D(4, 4, 4, comm=MPI.COMM_WORLD)

# Create a hierarchy with two refinements (3 levels in total)
hierarchy = GridHierarchy(coarse_grid, nrefinements=2)

# You can index the GridHierarchy like a normal list.
fine_grid = hierarchy[-1]

# Define the operator we want to apply
# Must inherit from AbstractOperator
class Poisson7pt(AbstractOperator):
    def __init__(self, grid):
        # Can do some stuff here, but remember to always do
        super().__init__(grid)

    # We need to implement this property. An @cached_property is like
    # an @property, but only gets evaluated once.
    @cached_property
    def diagonal(self):
        # This attribute is set by the superclass constructor
        grid = self.grid
        # Create storage of the diagonal vector
        D = self.grid.createGlobalVector()
        # Get write access to the process-local portion of the vector
        Darray = D.array
        # Fill it with some values
        Darray[:] = ...
        # Return the vector
        return D

    # We need to implement this method
    def mult(self, x, y):
        # x is the input vector, y is the output vector.
        # the grid object knows how to create a "ghosted" view of a
        # vector. Which we will likely need for x so that we can
        # access all the stencil values we need
        grid = self.grid
        # You might choose to make this in the __init__ method
        xlocal = grid.createLocalVector()
        # Fill xlocal with the ghosted representation of x.
        grid.globalToLocal(x, xlocal,
                           addv=PETSc.InsertMode.INSERT_VALUES)
        # Get read-only access to xlocal
        xarray = xlocal.array_r
        # Get read-write access to y
        yarray = y.array
        # Do the multiplication, putting values in y.

    # Finally, we need to implement this method
    def as_sparse_matrix(self):
        grid = self.grid
        # The grid also knows how to create a sparse matrix with data
        # allocated
        A = grid.createMatrix()
        # PETSc has facilities for setting matrix entries via a
        # stencil pattern
        row = PETSc.Mat.Stencil()
        col = PETSc.Mat.Stencil()
        # Loop over index extents
        for k, j, i in ...:
            # We set one row at a time.
            row.i = i
            row.j = j
            row.k = k
            # Figure out the column indices (e.g. i_ = i+1)
            for k_, j_, i_ in ...:
                col.i = i_
                col.j_ = j_
                col.k_ = k_
                value = ...
                A.setValueStencil(row, col, value,
                                  addv=PETSc.InsertMode.INSERT_VALUES)
        # Since inserting into a distributed matrix might require
        # communication of ghost data, at the end we do
        A.assemblyBegin(PETSc.Mat.AssemblyType.FINAL_ASSEMBLY)
        A.assemblyEnd(PETSc.Mat.AssemblyType.FINAL_ASSEMBLY)
        return A


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


Some one-dimensional tests are provided in `tests/test_one_dim.py`.
They presently do not pass, since the various bits of the `MGSolver`
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

## Part 1: An explicit solver

{{< hint info >}}
You should do your implementation for this part in a file called
`part1_explicit_euler.py` placed in the root of the repository.
{{< /hint >}}

Discretise the equation
$$
\partial_t u - \nabla \cdot K(x, y, z) \nabla u = f(x, y, z)
$$
using forward Euler as a timestepping scheme.

To do this, create a class `Poisson7pt` that discretises the spatial
operator using a 2nd order accurate 7-point stencil (as derived in lectures).
$$
-\nabla \cdot K(x, y, z) \nabla u.
$$

Using
$$
K(x, y, z) = \sin(4.5 \pi x)
$$
$$
f(x, y, z) = \frac{9 \pi}{2} \cos(4.5 \pi x),
$$
Dirichlet boundary conditions on the left and right faces
$$
u(x, y, z) = 0 \text{ at } x=0 \text{ and } x = 1
$$
and Neumann boundary conditions everywhere else
$$
\nabla u(x, y, z)\cdot n = 0,
$$
where $n$ is the outer normal to timestep to a steady state solution. The exact solution for this
problem is
$$
u^*(x, y, z) = x.
$$

{{< hint info >}}
Ensure that your implementation works correctly in parallel as well as
serial (when run with MPI).
{{< /hint >}}

{{< question >}}
How does the error in your numerical solution behave under grid
refinement?

What restriction, if any, is there on the size of the timestep you can
choose?
{{< /question >}}

### A higher-order scheme

{{< hint info >}}

This part doesn't need to you to write any code.

{{< /hint >}}

Derive, but do not implement, the 4th order accurate stencil for a
5-point discretisation of the Laplace operator in one dimension.

How do you have to modify the stencil at the boundary to maintain the
accuracy for:

1. Dirichlet conditions $u = g$
2. Neumann conditions $\nabla u \cdot n = h$


{{< question >}}

Would this spatial discretisation have the same timestep restriction
as the 2nd order operator, or a different one? Explain your answer.

{{< /question >}}

## Part 2: multigrid

Implement the missing pieces in the `MGSolver` class, namely 

- `MGSolver.jacobi`
- `MGSolver.vcycle`
- `MGSolver.wcycle`

Taking the same `Poisson7pt` operator that you implemented in Part 1,
we will now solve for the steady state directly (rather than
timestepping towards it).

{{< hint info >}}
You should do your implementation for this part in a file called
`part2_multigrid.py` placed in the root of the repository.
{{< /hint >}}

Confirm that your implementation is correct by doing an MMS
convergence test. For large problems you will probably want to run in
parallel.

{{< hint info >}}
If your operator definition was correct in parallel in Part 1, you
should not have to worry very hard about parallelism in this part,
since everything is done with "collective" operations.
{{< /hint >}}

{{< question >}}

For this problem, which method works best when you add more grid
levels? You can think of this both in terms of algorithmic convergence
and time to solution. Play around with the number of smoothing steps,
does that help.

{{< details "Performance hint" >}}

You may wish to pull the body of the matrix-vector `mult` method out
and try JIT-compiling it with numba. I found that made a big
(positive) difference in the performance of my code.

{{< /details >}}

{{< /question >}}


## Part 3: robustness

{{< hint info >}}
You should do your implementation for this part in a file called
`part3_variable_coefficient.py` placed in the root of the repository.
{{< /hint >}}

We will now look at how robust your solver is in the face of
coefficient variation that _does not_ align well with the grids.

For this setup, we'll solve the following problem. Meant to be an
idealised case of a machine room with hot and cold areas, along with
heat extraction from the boundary walls.

$$
$$

You can again adapt your `Poisson7pt` stencil to incorporate the new
coefficient variation.

Recall from lectures that when we have this kind of coefficient
variation, we can regain some robustness by using Galerkin coarse grid
operators. The `MGSolver` class supports this (say `galerkin=True`
when constructing an instance).

{{< question >}}

Compare the convergence behaviour of your multigrid scheme using
rediscretised coarse grids (the default) and Galerkin coarse grids.

Is there a setup with which you can regain the nice multigrid
efficiency that we saw previously?

Does your coarsest grid have to be larger?

Discuss your findings.

{{< /question >}}
