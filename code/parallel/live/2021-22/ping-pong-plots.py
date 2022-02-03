import numpy
from matplotlib import pyplot

ham8numpy_one_node = numpy.load("data/ham8-with-numpy-one-node.npy")
ham8numpy_two_node = numpy.load("data/ham8-with-numpy-two-node.npy")

ham8pickle_one_node = numpy.load("data/ham8-with-pickle-one-node.npy")
ham8pickle_two_node = numpy.load("data/ham8-with-pickle-two-node.npy")

ham7numpy_one_node = numpy.load("data/ham7-with-numpy-one-node.npy")
ham7numpy_two_node = numpy.load("data/ham7-with-numpy-two-node.npy")

pyplot.plot(ham8numpy_one_node[:, 0], ham8numpy_one_node[:, 1], "o-",
            label="Hamilton8 numpy, single node")

pyplot.plot(ham8numpy_two_node[:, 0], ham8numpy_two_node[:, 1], "o-",
            label="Hamilton8 numpy, two node")

pyplot.plot(ham8pickle_one_node[:, 0], ham8pickle_one_node[:, 1], "o-",
            label="Hamilton8 pickle, single node")

pyplot.plot(ham8pickle_two_node[:, 0], ham8pickle_two_node[:, 1], "o-",
            label="Hamilton8 pickle, two node")

pyplot.plot(ham7numpy_one_node[:, 0], ham7numpy_one_node[:, 1], "o-",
            label="Hamilton7 numpy, single node")

pyplot.plot(ham7numpy_two_node[:, 0], ham7numpy_two_node[:, 1], "o-",
            label="Hamilton7 numpy, two node")


axes = pyplot.gca()

axes.set_xscale("log")
axes.set_yscale("log")

pyplot.legend()
