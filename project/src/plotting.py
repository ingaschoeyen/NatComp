import matplotlib.pyplot as plt
from voting import *

# Plots voters and candidates, colours correspond to closest candidates
def plot_closest(voters : Population, candidates : Population, output_path : str = "./res_dis.png"):
    fig, ax = plt.subplots()
    ax.scatter(np.array(voters.popul)[:,0], np.array(voters.popul)[:,1], c=closest_points(voters.popul, candidates.popul, distance_euclid), alpha=1)
    ax.scatter(np.array(candidates.popul)[:,0], np.array(candidates.popul)[:,1], c=range(len(candidates.popul)), s=[200 for _ in range(candidates.size())], alpha=0.5)
    fig.savefig(output_path)

# Histogram of votes
# TODO make more colourful, or a pie chart, or just fancier in general
def plot_histogram(results : list[int], output_path : str = "./res_hist.png"):
    fig, ax = plt.subplots()
    ax.hist(results)

    ax.set_xlim([0, max(results)])

    ax = plt.gca()
    fig.savefig(output_path)

# TODO other types of plots
