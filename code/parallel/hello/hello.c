#include <stdio.h>
#include <mpi.h>

int main(void)
{
  int rank, size, len;
  MPI_Comm comm;
  char name[MPI_MAX_PROCESSOR_NAME];
  MPI_Init(NULL, NULL);
  comm = MPI_COMM_WORLD;
  MPI_Comm_rank(comm, &rank);
  MPI_Comm_size(comm, &size);
  MPI_Get_processor_name(name, &len);
  printf("Hello, World! I am rank %d of %d. Running on node %s\n",
         rank, size, name);
  MPI_Finalize();
  return 0;
}
