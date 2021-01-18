import argparse

import numpy
import scipy.optimize
from matplotlib import pyplot

parser = argparse.ArgumentParser()
parser.add_argument("output", type=str)

args, _ = parser.parse_known_args()
# Do Newton to find P such that 2log_2 P - (P-1) = 0
# We know that P = 1 is a solution, so we deflate that away
def f(p):
    return 1/abs(p-1) * (2*numpy.log2(p) - (p - 1))


root = scipy.optimize.newton(f, 2)

print(root)

fig, axes = pyplot.subplots(1)

Ps = numpy.linspace(0.5, 30, num=200)

axes.plot(Ps, Ps - 1, "b-", label="Ring reduction ($P-1$)")
axes.plot(Ps, 2*numpy.log2(Ps), "r--", label="Tree reduction ($2 \log_2 P$)")

axes.plot(root, root - 1, "o", markersize=5)

axes.set_xlabel("Number of processes")
axes.set_ylabel("Modelled time to compute reduction")
axes.legend(loc="best")

fig.savefig(args.output,
            orientation="landscape",
            transparent=True,
            bbox_inches="tight")
