from typing import Optional
import matplotlib.pyplot as plt
from voting import *

# Max 10
COLOURS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Max 26
CAND_NAMES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# Colours correspond to closest candidates

def scatter_voters_cands(ax : plt.Axes, voters : Population, candidates : Population, voter_colours : list[str], cand_colours : list[str]):
    ax.scatter(np.array(voters.popul)[:,0], np.array(voters.popul)[:,1],
               c=voter_colours,
               alpha=1)
    ax.scatter(np.array(candidates.popul)[:,0], np.array(candidates.popul)[:,1],
               c=cand_colours,
               s=[200 for _ in range(candidates.size())],
               alpha=0.5)
    ax.set_aspect('equal', adjustable='box')

def plot_closest(voters : Population, candidates : Population, cand_shifts : Optional[list[int]] = None, output_path : str = "./res_dis.png"):
    cand_shifts = [0 for _ in range(candidates.size())] if cand_shifts is None else cand_shifts
    fig, ax = plt.subplots()
    closest_colours = [COLOURS[p + cand_shifts[p]] for p in closest_points(voters.popul, candidates.popul, distance_euclid)]
    cand_colours = [COLOURS[i + cand_shifts[i]] for i in range(candidates.size())]
    scatter_voters_cands(ax, voters, candidates, closest_colours, cand_colours)
    fig.savefig(output_path)

def plot_approved(voters : Population, candidates : Population, threshold : float, radius_measure, output_path : str = "./res_dis.png"):
    fig, ax = plt.subplots()
    closest_colours = [COLOURS[p] for p in closest_points(voters.popul, candidates.popul, distance_euclid)]
    cand_colours = COLOURS[:candidates.size()]
    scatter_voters_cands(ax, voters, candidates, closest_colours, cand_colours)

    circles = [plt.Circle(voter, radius_measure(voter, candidates.popul, threshold), color=closest_colours[i], alpha=0.1) for i, voter in enumerate(voters.popul)]
    for circle in circles:
        ax.add_patch(circle)

    fig.savefig(output_path)

def plot_pie(results : list[int], cand_shifts : Optional[list[int]] = None, output_path : str = "./res_pie.png"):
    cand_shifts = [0 for _ in range(len(results))] if cand_shifts is None else cand_shifts
    cand_colours = [COLOURS[i + cand_shifts[i]] for i in range(len(results))]
    cand_names = [CAND_NAMES[i + cand_shifts[i]] for i in range(len(results))]
    fig, ax = plt.subplots()
    ax.pie(x=results, labels=cand_names, colors=cand_colours,
           autopct=lambda p : '{:.2f}%  ({:,.0f})'.format(p,p * sum(results)/100))
    fig.savefig(output_path)

def plot_bar(results : list[int], cand_shifts : Optional[list[int]] = None, output_path : str = "./res_bar.png"):
    cand_shifts = [0 for _ in range(len(results))] if cand_shifts is None else cand_shifts
    cand_colours = [COLOURS[i + cand_shifts[i]] for i in range(len(results))]
    cand_names = [CAND_NAMES[i + cand_shifts[i]] for i in range(len(results))]
    fig, ax = plt.subplots()
    ax.bar(x=cand_names, height=results, color=cand_colours)
    fig.savefig(output_path)

# TODO other types of plots
# TODO plot quality (VSE) dependent on parameters of system
