# Introducing DMDA objects
import sys

import petsc4py
from mpi4py import MPI

petsc4py.init(sys.argv)

# Get access to PETSc
from petsc4py import PETSc  # noqa: E402

comm = MPI.COMM_WORLD

PETSc.Sys.popErrorHandler()

# The global grid is going to have NX points in X direction, NY points
# in Y direction.
NX = 3
NY = 5

# There are individual functions that we can use to set each of these
# things, but it's easier to just set them in the constructor.
grid = PETSc.DMDA().create(dof=1,  # Each grid point will contain one double
                           sizes=(NX, NY),  # Global size
                           # Stencil type: tells us how to create matrices
                           stencil_type=PETSc.DMDA.StencilType.STAR,
                           # Width of stencil
                           stencil_width=1,
                           comm=comm,
                           # Call setup separately.
                           setup=False)
# As usual we set from options and then setup.
grid.setFromOptions()
grid.setUp()

# If your system has X11 on it, then when you configure PETSc, it
# builds with X-windows, and you can say -grid_view draw to draw a
# picture.
# The conda package doesn't have this support.
grid.viewFromOptions("-grid_view")

# We can make a matrix that is correctly allocated for the star stencil.
mat = grid.createMatrix()
# We can view it, again -mat_view draw will work with X11
# Use -draw_pause 5 to leave it on screen for 5 seconds.
mat.viewFromOptions("-mat_view")

# We can refine grids.
refined = grid.refine()
refined.viewFromOptions("-ref_grid_view")

# Create a prolongator for a 2nd order finite difference
# discretisation (stencil width of 1) from grid to refined grid.
# createInterpolation produces two things, the prolongation matrix
# and a vector for "scaling" the prolongation.
# ASIDE:
# What is the scaling doing?
# We can use prolongation transposed to restrict residuals in a
# multigrid cycle. If we want to restrict "primal" quantities, so for
# example a variable coefficient. Then, the restriction matrix does
# the wrong thing, that can be "fixed" by dividing by "rscale".
# Better -> use grid.createInjection(refined).
# END ASIDE
prolongation, rscale = grid.createInterpolation(refined)

# This doesn't work for DMDA, instead use the prolongation matrix in
# its transpose form.
# restrict = grid.createRestriction(refined)
# restrict.viewFromOptions("-restrict_view")

# Let's get some vectors
vcoarse = grid.createGlobalVector()
vcoarse.setRandom()
vcoarse.viewFromOptions("-coarse_view")
vfine = refined.createGlobalVector()

prolongation.mult(vcoarse, vfine)
vfine.viewFromOptions("-fine_view")

# Restriction of residuals, moves dual things. Transpose of the
# prolongation.
# o---x---o---x---o fine grid in 1D
# |  / \  |  / \  |
# V v   v V v   v V takes linear combinations of o and x points
# |/     \|/     \|
# o-------o-------o coarse grid in 1D
prolongation.multTranspose(vfine, vcoarse)

# If we want to transfer primal things, we should use injection
inject = grid.createInjection(refined)
# inject is a matrix that transfers from fine to coarse with matmult
# Picks out dofs on fine grid that match up with coarse dofs.
#
# o---x---o---x---o fine grid in 1D
# |       |       |
# V       V       V transfer values (ignore values from x points)
# |       |       |
# o-------o-------o coarse grid in 1D
inject.viewFromOptions("-inject_view")
inject.mult(vfine, vcoarse)
vcoarse.viewFromOptions("-coarse_view")


# ghost vectors
# This has enough space for all the entries, plus the ghost entries
# PETSc allocates space for a square box for both STAR and BOX
# stencils, but for STAR stencils the corners are not filled with
# values.
# This is a vector on COMM_SELF.
vghost = grid.createLocalVector()

# Insert values from the global vector into the ghost vector, filling
# the ghost region with the correct off-process entries.
grid.globalToLocal(vcoarse, vghost,
                   addv=PETSc.InsertMode.INSERT_VALUES)

vghost.viewFromOptions("-ghost_view")

PETSc.Sys.syncPrint(f"[{comm.rank}] global: {vcoarse.getSizes()}, "
                    f"local: {vghost.getSizes()}",
                    comm=comm)
PETSc.Sys.syncFlush(comm=comm)

# For nice indexing, there's an example in the coursework repo in
# 1D, and I'll do more next week.
# Readonly access
coarse_array = vcoarse.array_r

# Read write access
ghost_array = vghost.array

# For nice indexing, want to turn these into 2D arrays
# Remember picture, this tells us the extent of the local patch
# I am ignoring the first return value for now, but will return to it
# next time.
_, (xm, ym) = grid.getCorners()
# And the same with ghosts
_, (gxm, gym) = grid.getGhostCorners()

# "Fortran" order! (y, x)
coarse_array = coarse_array.reshape(ym, xm)
# "Fortran" order!
ghost_array = ghost_array.reshape(gym, gxm)

PETSc.Sys.syncPrint(f"[{comm.rank}] shapes global: {coarse_array.shape}, "
                    f"local: {ghost_array.shape}",
                    comm=comm)
PETSc.Sys.syncFlush(comm=comm)
