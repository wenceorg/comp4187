# We've seen a bunch of theory and ideas behind parallel data
# structures. Now we're going to look at some implementation. Building
# this stuff from scratch is a bad idea, so we're going to look at the
# concepts in the PETSc library. https://www.mcs.anl.gov/petsc/

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

# Remove the petsc4py error handler, and just use the normal PETSc one.
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
# https://www.mcs.anl.gov/petsc/petsc-current/docs/manualpages/Vec/index.html
# Translation from petsc4py -> PETSc
# All PETSc Vec methods are called VecXyz e.g. VecCreate, VecNorm.
# remove the Vec prefix (lowercase the first letter, and keep
# camelcase for the rest)
# See the course webpages for a PETSc -> petsc4py rosetta stone.
v1 = PETSc.Vec().create(comm=comm)  # Calls VecCreate.
v2 = PETSc.Vec().create(comm=comm)

# How many entries should we have?
# This makes space for the vector metadata but we haven't said how
# much space it should have.

# Make a vector that holds 10 values in total (distributed
# approximately evenly across the available processes in the
# communicator).

# This is logically collective: everyone has to agree that the vector
# has global size 10.
# We can either specify the global size (and PETSc will figure out a
# partition of the local sizes)
v1.setSizes((None,              # local size on this rank
             10))               # global size

# Or we can say how many entries we want. And PETSc can figure out how
# many entries there are in total.
# Or we can specify the local size on each process and PETSc will sum
# them to produce the global size
v2.setSizes((1 + comm.rank*10,  # local size on this rank
             None))             # global size


# We can control aspects of the way objects behave by configuring them
# with commandline options.
# Generally not necessary for vectors.

# To distinguish objects from one an another (e.g. we don't want the
# same options for v1 and v2) we can give every PETSc object a unique
# "options prefix"

v1.setOptionsPrefix("v1_")
v2.setOptionsPrefix("v2_")

# Can do this on all PETSc objects
# Look up in the command line flags for any configuration for this object.
v1.setFromOptions()
v2.setFromOptions()

# Once we're done getting things ready, we can set the objects up for
# use.
# Allocates space for the vector.
v1.setUp()
v2.setUp()

# Let's look at the sizes we've ended up with
# PETSc's syncPrint prints in a synchronised manner on all processes
# Output comes after a syncFlush.
PETSc.Sys.syncPrint(f"[{comm.rank}]: "
                    f"v1: {v1.getSizes()}; "
                    f"v2: {v2.getSizes()}",
                    comm=comm)
PETSc.Sys.syncFlush(comm=comm)


# We can manipulate local entries by getting a numpy array wrapping
# the local values
# This is a _logically collective_ operation. No synchronisation
# between processes is performed, but every process needs to
# participate because this modifies some state counters.
v1array = v1.array

v1array[:] = 1 + comm.rank

# This will look for a flag -v1_vec_view and view the vector
v1.viewFromOptions("-vec_view")


# If you only need read-only access to the array, use array_r. array_r
# is not collective.
v1array_ro = v1.array_r
v2.array[:] = sum(v1array_ro)

v2.viewFromOptions("-vec_view")

# We can do various pointwise operations on vectors
# The vectors involved must have a _compatible layout_
# v1 has 10 global entries, v2 is not compatible with this.
# v1.axpy(1, v2) # <- would fail

# We can get a vector with the same layout with duplicate
v3 = v2.duplicate()
# This gets an empty options prefix
v3.setOptionsPrefix("v3_")
v3.viewFromOptions("-vec_view")

# Or we can also copy values

v4 = v2.copy()
v4.setOptionsPrefix("v4_")
# Pointwise operations need us to have allocated all the vectors.

# https://www.mcs.anl.gov/petsc/petsc-current/docs/manualpages/Vec/VecAXPY.html#VecAXPY
# C version  VecAXPY(Vec y,PetscScalar alpha,Vec x)
# We would write VecAXPY(v4, 0.5, v2)
# To translate, first (object) argument is the object we call the
# method on. v4.axpy(0.5, v2) remaining arguments appear in order
# v4 <- 0.5 v2 + v4 "alpha x plus y"
# In place modification of v4.
v4.axpy(0.5, v2)

# v4 <- v2 + 0.25 v4 "alpha y plus x"
v4.aypx(0.25, v2)
v4.viewFromOptions("-vec_view")
# We can also do reductions of various kinds
# Again, these need compatible layout where more than one vector is
# provided.
v4v2dot = v4.dot(v2)

# Collective print, only rank 0 on the communicator actually prints
# anything
PETSc.Sys.Print(f"v4 . v2 = {v4v2dot}", comm=comm)

# We can also take euclidean norms
#  VecNorm(Vec x,NormType type,PetscReal *val)
# Translation of these enums (like NormType) is that they are
# namespaced just in PETSc.NormType

# l1 norm: sum_i |x_i|
v4_1 = v4.norm(norm_type=PETSc.NormType.NORM_1)
# l2 norm: sqrt(sum_i |x_i|^2)
v4_2 = v4.norm(norm_type=PETSc.NormType.NORM_2)
# linf norm: max_i |x_i|
v4_inf = v4.norm(norm_type=PETSc.NormType.INF)

PETSc.Sys.Print(f"||v4||_1 = {v4_1}", comm=comm)
PETSc.Sys.Print(f"||v4||_2 = {v4_2}", comm=comm)
PETSc.Sys.Print(f"||v4||_inf = {v4_inf}", comm=comm)

# Insertion of values that are not local. Generally we don't need to
# do this, but this will illustrate a common pattern.
# Recall that we don't want to communicate all the time, and instead
# batch things up.
# PETSc provides an interface for this via Vec.setValues
# https://www.mcs.anl.gov/petsc/petsc-current/docs/manualpages/Vec/VecSetValues.html
# VecSetValues(Vec x,PetscInt ni,const PetscInt ix[],const PetscScalar y[], InsertMode iora)

# The global size of the vector
size = v2.getSize()
# The local size
lsize = v2.getLocalSize()

# Make everything 0 first.
v2.set(0)

# 10 random indices
rng = numpy.random.default_rng()
indices = rng.integers(size, size=10,
                       # The type for integers in petsc.
                       dtype=PETSc.IntType)
values = rng.uniform(size=10)

PETSc.Sys.syncPrint(f"{indices} {values}", comm=comm)
PETSc.Sys.syncFlush(comm=comm)

# Naively everyone has to communicate all the time.
# PETSc batches up insertion to indices I don't own.
# As soon as we start doing VecSetValues, it is invalid to look at the
# values in the vector.
v2.setValues(indices, values, addv=PETSc.InsertMode.ADD_VALUES)

# Then we have to _finalise_ the insertion.
v2.assemblyBegin()              # Starts the batched send/recv
# In between you can do some stuff that doesn't touch v2.
# PETSc splits all of its communications into begin and end.
# This waits on the send/recv and inserts locally.
v2.assemblyEnd()

# After the assemblyEnd we are permitted to look at the vector again.

v2.viewFromOptions("-vec_view_after")
