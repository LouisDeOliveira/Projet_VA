import numpy as np
import matplotlib.pyplot as plt


def show_XY_graph(X, Y):
    X = X[:len(Y)]
    plt.plot(X, Y)
    plt.show()
