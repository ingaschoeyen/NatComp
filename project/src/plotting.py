import matplotlib.pyplot as plt
from voting import *

# Plots voters and candidates, colours correspond to closest candidates
def plot_closest(voters : Population, candidates : Population, output_path : str = "./res_dis.png"):
    plt.scatter(voters.pop[:,0], voters.pop[:,1], c=closest_points(voters.pop, candidates.pop, distance_euclid), alpha=1)
    plt.scatter(candidates.pop[:,0], candidates.pop[:,1], c=range(len(candidates.pop)), s=[200 for _ in range(len(candidates.pop))], alpha=0.5)
    plt.savefig(output_path)

# Histogram of votes
# TODO make more colourful, or a pie chart, or just fancier in general
def plot_histogram(results : list[int], output_path : str = "./res_hist.png"):
    fig, ax = plt.subplots()
    ax.hist(results)

    ax.set_xlim([0, max(results)])

    ax = plt.gca()
    plt.savefig(output_path)

# TODO other types of plots
