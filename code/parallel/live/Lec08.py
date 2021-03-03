import sys

import petsc4py
from mpi4py import MPI

petsc4py.init(sys.argv)

# Get access to PETSc
from petsc4py import PETSc  # noqa: E402

comm = MPI.COMM_WORLD

PETSc.Sys.popErrorHandler()

# Represents a finite-dimensional linear operator
mat = PETSc.Mat().create(comm=comm)

# Let's specify the number of local rows and columns on each process.
lrows = 3
lcols = 4
mat.setSizes(((lrows, None),    # rows (local, global)
              (lcols, None)))   # cols (local, global)

# As with the vectors, we can set an options prefix.
mat.setOptionsPrefix("m1_")
mat.setFromOptions()
# And set things up.
mat.setUp()
PETSc.Sys.syncPrint(f"[{comm.rank}]: {mat.getSizes()}", comm=comm)
PETSc.Sys.syncFlush(comm=comm)

# Setting values.
# This is an interface to say A[i, j] = v (with INSERT_VALUES)
# Or                          A[i, j] += v (with ADD_VALUES)
# Can set blocks.
# Here we are saying          A[[0, 2], [2, 3]] = [[1, 2], [3, 4]]
if comm.rank == 0:
    # Logically collective, here we're doing it on rank 0, everyone
    # must agree on the insertion mode.
    mat.setValues([0, 2], [2, 3], [1, 2, 3, 4],
                  addv=PETSc.InsertMode.INSERT_VALUES)

# To finish up, like with Vec.setValues, we need to "assemble" the matrix
# This is going to package up and send entries to remote processes.
# This also calls mat.viewFromOptions
mat.assemblyBegin(PETSc.Mat.AssemblyType.FINAL_ASSEMBLY)
# Can do work here that doesn't touch mat.
mat.assemblyEnd(PETSc.Mat.AssemblyType.FINAL_ASSEMBLY)

# Preallocation
# Insertion into a sparse matrix requires dynamic memory allocation
# We can avoid that if we say how many non-zero entries we intend to use
# If we create matrices via a DMDA, we don't have to worry about this
# (we'll see that next time).
m2 = PETSc.Mat().create(comm=comm)
m2.setSizes(((lrows, None),
             (lcols, None)))
m2.setOptionsPrefix("m2_")
m2.setFromOptions()
# There will be three non-zeros per row.
m2.setPreallocationNNZ(3)
m2.setUp()

# Doesn't make sense for parallel if it is only rank 0 putting in
# entries, so we can ask which rows (and columns if we like) we own,
# and then insert in parallel.

# Which rows do I own?
rstart, rend = m2.getOwnershipRange()

PETSc.Sys.syncPrint(f"[{comm.rank}]: owned rows: [{rstart}, {rend})",
                    comm=comm)
PETSc.Sys.syncFlush(comm=comm)

# PETSc just discards insertions to negative rows and columns.
for row in range(rstart, rend):
    # Setvalues interfaces operates with _global_ indexing.
    # So we provide globally numbered entries to set (or add) values
    # to.
    # For grid-based PDE stuff, it's often more natural to think in
    # terms of process-local numbering, and petsc has a
    # mat.setValuesLocal interface for this, which we'll see when we
    # create matrices via a DMDA next time.
    m2.setValue(row, row, comm.rank + 1)
    m2.setValue(row, row-1, -(comm.rank + 1))
    m2.setValue(row, row-2, -(comm.rank + 1)*10)

m2.assemblyBegin(PETSc.Mat.AssemblyType.FINAL_ASSEMBLY)
m2.assemblyEnd(PETSc.Mat.AssemblyType.FINAL_ASSEMBLY)

# Matrix operations

# Matrix-vector operations.

# Need compatible vectors

# If I want to compute y = Ax, then this is the right order
# See https://www.mcs.anl.gov/petsc/petsc-current/docs/manualpages/Mat/MatCreateVecs.html
x, y = m2.createVecs()

y1 = m2.createVecLeft()
x1 = m2.createVecRight()

x.set(comm.rank+1)

x.setOptionsPrefix("x_")
# x.viewFromOptions("-vec_view")

# y <- A x
m2.mult(x, y)

y.setOptionsPrefix("y_")
y.viewFromOptions("-vec_view")

# Can also do transpose multiplication

# x <- A^T y
# x <- x + A^T y
m2.multTranspose(y, x)
# This is useful for prolongation of the correction in multigrid.
# u <- u + P c
# multTransposeAdd(x, y, z): z <- A^T x + y
m2.multTransposeAdd(y, x, x)
x.viewFromOptions("-vec_view")
