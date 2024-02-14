import sys

import petsc4py
from mpi4py import MPI

petsc4py.init(sys.argv)

# Get access to PETSc
from petsc4py import PETSc  # noqa: E402

comm = MPI.COMM_WORLD

PETSc.Sys.popErrorHandler()

# matrix-vector products
# assembling matrices

NX = 9
grid = PETSc.DMDA().create(dof=1,
                           sizes=(NX, ),
                           stencil_type=PETSc.DMDA.StencilType.STAR,
                           stencil_width=1,
                           comm=comm,
                           setup=False)

# |<Hx>|
# o----o----o----o----o----o----o----o----o
# 0    1    2    3    4    5    6    7    8

# Division between two processes

#     Rank 0           Ghost point
# o----o----o----o-----O
# 0    1    2    3
#
#
#                0     1    2    3    4    5 <- ighost == ilocal + (xstart - xstartghost)
#                      0    1    2    3    4 <- ilocal
#                             Rank 1
#                O-----o----o----o----o----o
#       Ghost point    4    5    6    7    8
#                      xstart
#                      |<-------- nx ----->|
#          xstartghost
#                |<-------- nxghost ------>|
grid.setFromOptions()
grid.setUp()

# Let's discretise the 1D constant-coefficient laplacian.
# -∇^2 u = b
# We're going to do the action ∇^2 x, and we're going to assemble the
# sparse matrix representing ∇^2.
#
# stencil is [-1/Hx, 2/Hx, -1/Hx]

# We're going to compute y \gets Ax
# So we need vectors for x and y.

x = grid.createGlobalVector()
y = grid.createGlobalVector()

# Put our rank in x.
x.array[:] = comm.rank + 1


def Ax(grid, x, y):
    # To do the stencil computation, we need a ghosted version of x,
    # so let's make one.
    xloc = grid.createLocalVector()
    grid.globalToLocal(x, xloc, addv=PETSc.InsertMode.INSERT_VALUES)

    # We need the grid spacing
    # If we were 2D, then we would say (mx, my) = grid.getSizes()
    #            3D,                   (mx, my, mz) = grid.getSize()
    # Global number of points in each cartesian direction
    mx, = grid.getSizes()

    Hx = 1 / (mx - 1)

    # Corners of owned part of domain
    (xstart, ), (nx, ) = grid.getCorners()

    # Corners with ghost region
    (xstartghost,), (nxghost,) = grid.getGhostCorners()

    # We'll read this one
    # If we're in 2D, then the ordering is "y, x", so we would do:
    # xloc.array_r.reshape(nyghost, nxghost)
    # Then we would index with [j, i]
    # And do a loop for j in range(nyghost) for i in range(nxghost)
    xarray = xloc.array_r.reshape(nxghost)

    # And write to here
    yarray = y.array.reshape(nx)

    # For every point that we own.
    for ilocal in range(nx):
        # global point in the domain
        iglobal = ilocal + xstart
        # index into ghost vector corresponding to ilocal
        ighost = ilocal + xstart - xstartghost

        # Diagonal part of stencil 1/Hx [-1, 2, -1]
        yarray[ilocal] = 2/Hx * xarray[ighost]

        if iglobal == 0 or iglobal == mx - 1:
            # We're on the global boundary, and applying Dirichlet
            # conditions so we're done.
            pass
        else:
            # Left part of stencil
            yarray[ilocal] += -1/Hx * xarray[ighost-1]
            # Right part of stencil
            yarray[ilocal] += -1/Hx * xarray[ighost+1]

    # That's it. We have the correct output values for all points we
    # own, so no more communication to do.
    return

Ax(grid, x, y)

x.viewFromOptions("-x_view")
y.viewFromOptions("-y_view")

# Now let's make the matrix

mat = grid.createMatrix()


def Astencil(grid, mat):
    mx, = grid.getSizes()
    Hx = 1/(mx - 1)
    # This time we will only need the global indices
    (xstart, ), (nx, ) = grid.getCorners()

    # These stencil objects work with _global_ indices.
    row = PETSc.Mat.Stencil()
    col = PETSc.Mat.Stencil()
    # We can set row.i, row.j, row.k to indicate the point in 3D space.

    # We will insert values in owned rows, one row at a time.
    for iglobal in range(xstart, nx+xstart):
        # If we were 2D, we'd say
        # row.i = iglobal
        # row.j = iglobal
        # col.i = iglobal
        # col.j = iglobal
        # For the diagonal entry.
        row.i = iglobal
        col.i = iglobal
        value = 2 / Hx

        # Always insert diagonal
        mat.setValueStencil(row, col, value,
                            addv=PETSc.InsertMode.INSERT_VALUES)

        if iglobal == 0 or iglobal == mx - 1:
            # We're on the global boundary, and applying Dirichlet
            # conditions so we're done.
            # Non-symmetric imposition of the boundary condition
            # We zero the off diagonal row corresponding to a boundary
            # dof, but _not_ the column. This is easier to think
            # about/implement.
            # For multigrid, what you normally want to do in this
            # situation is have the boundary row "scaled compatibly"
            # with the rest of the discretisation.
            # That is, I don't put a literal 1 here, but rather 2/Hx:
            # then I don't have to think about what's going on with
            # the right hand side.
            # This also plays well with the built in restrict/prolong
            # from the DMDA grid which don't know about boundary
            # conditions.
            pass
        else:
            col.i = iglobal - 1
            value = -1/Hx
            mat.setValueStencil(row, col, value,
                                addv=PETSc.InsertMode.INSERT_VALUES)
            col.i = iglobal + 1
            mat.setValueStencil(row, col, value,
                                addv=PETSc.InsertMode.INSERT_VALUES)

    mat.assemblyBegin(mat.AssemblyType.FINAL_ASSEMBLY)
    mat.assemblyEnd(mat.AssemblyType.FINAL_ASSEMBLY)


# Another option, using local indexing
def Alocal(grid, mat):
    mx, = grid.getSizes()
    Hx = 1/(mx - 1)
    (xstart, ), (nx, ) = grid.getCorners()
    (xstartloc, ), (nxloc, ) = grid.getGhostCorners()

    # We will insert values in owned rows, one row at a time.
    # This approach is fiddlier for higher dimensions, because there's
    # no support for (i, j) indexing, you've got to unroll it by hand,
    # so it's kind of easy to get wrong.
    # The MatStencil approach above does that unrolling for you.
    for ilocal in range(nx):
        iglobal = ilocal + xstart
        ighost = ilocal + xstart - xstartloc
        # Careful, the local insertion needs to work with ghosted
        # indices, not the non-overlapped local indices.
        if iglobal == 0 or iglobal == mx - 1:
            # We're on the global boundary, so just insert diagonal
            # conditions and we're done.
            values = [2/Hx]
            rows = [ighost]
            cols = [ighost]
            mat.setValuesLocal(rows, cols, values,
                               addv=PETSc.InsertMode.INSERT_VALUES)
        else:
            values = [-1/Hx, 2/Hx, -1/Hx]
            rows = [ighost]
            cols = [ighost-1, ighost, ighost+1]
            mat.setValuesLocal(rows, cols, values,
                               addv=PETSc.InsertMode.INSERT_VALUES)

    mat.assemblyBegin(mat.AssemblyType.FINAL_ASSEMBLY)
    mat.assemblyEnd(mat.AssemblyType.FINAL_ASSEMBLY)


matlocal = grid.createMatrix()

# Create the operator via two different approaches
# The Stencil approach is probably easier to handle for
# multi-dimensional grids, since you don't need to unroll the indexing
# by hand.
Astencil(grid, mat)
Alocal(grid, matlocal)

# Check they're the same!
mat.viewFromOptions("-stencil_view")
matlocal.viewFromOptions("-local_view")

# And use one to compute y <- Ax
matlocal.mult(x, y)
y.viewFromOptions("-y_view")
