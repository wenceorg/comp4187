import argparse
import sys

from mpi4py import MPI
from numpy.random import default_rng


def run(npts, comm=MPI.COMM_WORLD):
    rng = default_rng()
    pts = rng.uniform(low=0, high=1, size=(npts, 2))
    inside = ((pts[:, 0]**2 + pts[:, 1]**2) < 1).sum()
    return 4*inside/npts


def main(name, *argv):
    parser = argparse.ArgumentParser(
        description="Compute an approximation to pi using Monte-Carlo")
    parser.add_argument("N", type=int, help="Number of points to draw")
    args, _ = parser.parse_known_args(args=argv)
    comm = MPI.COMM_WORLD
    mypi = run(args.N, comm=comm)
    if comm.rank == 0:
        print(f"Pi is approximately {mypi}")


if __name__ == "__main__":
    main(*sys.argv)
