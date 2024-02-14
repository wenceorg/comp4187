# We've seen a bunch of theory and ideas behind parallel data
# structures. Now we're going to look at some implementation. Building
# this stuff from scratch is a bad idea, so we're going to look at the
# concepts in the PETSc library. https://petsc.org/

# To get access to commandline arguments
import sys

# Later we will initialise some vectors with random values
import numpy.random
# We will also want PETSc (via petsc4py)
# To get this from conda:
# - conda install -c conda-forge petsc4py
# To get it with pip (not using conda) do
# - pip install petsc4py
# (this will go away and build PETSc and petsc4py which might take a
# while).
import petsc4py
# As usual, we need MPI, but not that much of it, actually.
from mpi4py import MPI

# By doing this, we will make PETSc aware of any commandline arguments
# we pass. This will be used to configure the objects
petsc4py.init(sys.argv)

# Get access to PETSc
from petsc4py import PETSc  # noqa: E402

comm = MPI.COMM_WORLD

# Remove the petsc4py error handler, and just use the normal PETSc
# one.
# If you want to debug in parallel with pdb (I recommend either pdb++
# or ipython --pdb) then you'll want to remove this.
# For parallel debugging with a small number of cores I like a
# combination of tmux and https://github.com/wrs20/tmux-mpi
# Running tmux-mpi 2 ipython --pdb my-script.py
# gives me a tmux window where I can run all the processes in parallel
# and debug.
PETSc.Sys.popErrorHandler()

# PETSc has a number of objects useful for numerical computing. It is
# a large C library written in an object-oriented manner, with some
# idiosyncracies.

# For our purposes, it provides
# 1. distributed vectors (via the Vec class) <--
# 2. distributed sparse matrices (via the Mat class) <--
# 3. distributed structured grids (via the DMDA class) <--
# 4. hierarchies of grids (refinement of DMDA objects) <--
# 5. a large configurable interface to linear solvers (via the KSP
#    class)

# We will not cover:
# - a bunch of lower-level communication and index-management objects
#   which we won't need because they'll be provided by the DMDA.
# - nonlinear solvers (via SNES)
# - unstructured grids (via DMPlex)
# - timestepping methods (via TS)
# - optimisation (via TAO)


# Let's make some vectors

# PETSc documentation:
# https://petsc.org/release/docs/manualpages/Vec/index.html

# PetscErrorCode  VecCreate(MPI_Comm comm, Vec *vec)

# Translation:

# VecCreate is a _method_ on Vec objects. And camel-cased names are
# maintained but the first letter is lowercase.
# So: VecCreate -> Vec()

v1 = PETSc.Vec()                # Create empty object

v1.create(comm=comm)            # Call create method.

# Vec().create(comm=comm) equivalent to __init__ on a normal Python object.

# How big will the vector be?

# PetscErrorCode  VecSetSizes(Vec v, PetscInt n, PetscInt N)
# n is number of entries on _this process_
# N is total number of entries.

n = 3
N = 10
# Sizes are provided as a tuple of (local, global)
# Let's say we know the local size, but want PETSc to determine the global size
v1.setSizes((n, None))
# Now v1 global size is sum_ranks n

# Equally, if we know the global size can say

v2 = PETSc.Vec().create(comm=comm)
# N elements will be divided approximately equally amongst all the ranks.
v2.setSizes((None, N))

# All PETSc objects are configured by an options database (command-line arguments)

# Configure objects via options:

# All objects by default have the same (empty) _prefix_.
# Set a prefix to provide different options for different objects

v1.setOptionsPrefix("v1_")
v2.setOptionsPrefix("v2_")
v1.setFromOptions()
v2.setFromOptions()

PETSc.Sys.syncPrint(f"[{comm.rank}] {v1.getSizes()} {v2.getSizes()}", comm=comm)
PETSc.Sys.syncFlush(comm=comm)

# Setting values

# Two ways of doing this:

# 1. Directly write to local part of vector

# .array property gets writeable numpy array for locally owned values
# This is (logically) collective: every process in the communicator needs to access the property
# otherwise -> deadlock (or wrong results). (https://petsc.org/release/docs/manualpages/Vec/VecGetArray.html)
v1.array[0] = 1
# If you want only read-only access to the local part use v1.array_r
# (note trailing _r), which is _not_ collective
# https://petsc.org/release/docs/manualpages/Vec/VecGetArrayRead.html

v1.viewFromOptions("-vec_view")

PETSc.Sys.syncPrint(f"[{comm.rank}] ||v1|| =  {v1.norm()}", comm=comm)
PETSc.Sys.syncFlush(comm=comm)

# 2. Write through an interface to any (globally numbered) entry.

if comm.rank == 0:
    # PetscErrorCode  VecSetValues(Vec x,PetscInt ni,const PetscInt ix[],const PetscScalar y[],InsertMode iora)
    # Need to provide
    # Array of indices (in global numbering)
    # Array of values (of same length)

    # Insertion mode: PETSc.InsertMode.INSERT
    # either v1[i] = value[i]
    # or PETSc.InsetMode.ADD
    # v1[i] = v1[i] + value[i]
    # Insertion mode is logically collective (can't mixed INSERT and
    # ADD on different processes in one go).
    # https://petsc.org/release/docs/manualpages/Vec/VecSetValues.html
    v1.setValues([11], [100], addv=PETSc.InsertMode.INSERT)

# So now, we've scheduled an insertion, but haven't "committed" it
# yet.

# Finalise insertions with
# https://petsc.org/release/docs/manualpages/Vec/VecAssemblyBegin.html
v1.assemblyBegin()
# These are split, because you could overlap some communication with
# compute in between here.

# This synchronises neighbourhood-wise (so it does pointwise
# synchronisation over the processes that are exchanging values).
# https://petsc.org/release/docs/manualpages/Vec/VecAssemblyEnd.html
v1.assemblyEnd()

# Pointwise operations on vectors:

# v1 <- 10*v2 + v1 (pointwise)
# These operations must have vectors with compatible layouts (each
# process must have then same number of entries for every vector)
# This would fail because v1 and v2 are not compabtible.
if False:
    # https://petsc.org/release/docs/manualpages/Vec/VecAXPY.html
    v1.axpy(10, v2)
