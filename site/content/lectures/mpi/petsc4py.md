---
title: "PETSc and petsc4py"
weight: 5
---

# A petsc4py Rosetta stone

[PETSc](https://petsc.org/release) itself has rather good
documentation, both of the
[API](https://petsc.org/release/docs/manualpages/) and a
[user manual](https://petsc.org/release/docs/manual/). The PETSc API
has very consistent naming. Objects are created with `XXXCreate`.
Where `XXX` stands for the object type name. For example, to create a
vector (which has type
[`Vec`](https://petsc.org/release/docs/manual/vec/)):
```c
Vec v;
VecCreate(MPI_COMM_WORLD, &v);
```
To create a matrix (which has type
[`Mat`](https://petsc.org/release/docs/manual/mat)):
```c
Mat m;
MatCreate(MPI_COMM_WORLD, &m);
```

In python-land, all object names are the same, and namespaced within
the `PETSc` package. To create a type `XXX` we do `PETSc.XXX()` to
allocate space for the object and then call the `create` method. For
example, to create a new vector
```python
from petsc4py import PETSc
from mpi4py import MPI
v = PETSc.Vec().create(comm=MPI.COMM_WORLD)
```
and to create a new matrix
```python
from petsc4py import PETSc
from mpi4py import MPI
m = PETSc.Mat().create(comm=MPI.COMM_WORLD)
```

Subsequent "method" calls on the created objects take as their first
argument the object on which to call the method. For example
[`VecSetValues`](https://petsc.org/release/docs/manualpages/Vec/VecSetValues.html)
has prototype
```c
VecSetValues(Vec x,PetscInt ni,const PetscInt ix[],const PetscScalar y[],InsertMode iora);
```

To translate this to `petsc4py`:

1. Remove the type name prefix from the method name `VecSetValues ->
   SetValues`
2. lowercase the first letter `SetValues -> setValues`
3. Use this as a method of the `Vec` object you want

Since arrays know their size in Python, we can avoid the `ni` argument
that says how many entries we are inserting. The
[`InsertMode`](https://petsc.org/release/docs/manualpages/Sys/InsertMode.html#InsertMode)
enum type turns into a enum in `PETSc`. So `PETSc.InsertMode`

```python
v.setValues(indices, values, addv=PETSc.InsertMode.ADD_VALUES)
```
I find it often useful to have an IPython window open where I can
autocomplete method names and look at their signatures.

We will see more examples in the live-coding parts of the lectures.
