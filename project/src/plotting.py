from typing import Any, Optional
import matplotlib.pyplot as plt
from voting import *

# Max 10
COLOURS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Max 26
CAND_NAMES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# Colours correspond to closest candidates
def scatter_agent_points(ax : plt.Axes, voters_points : list[Point], candidates_points : list[Point],
                         voter_colours : list[str], cand_colours : list[str]):
    ax.scatter(np.array(voters_points)[:,0], np.array(voters_points)[:,1],
               c=voter_colours,
               alpha=1)
    ax.scatter(np.array(candidates_points)[:,0], np.array(candidates_points)[:,1],
               c=cand_colours,
               s=[200 for _ in range(len(candidates_points))],
               alpha=0.5)
    ax.set_aspect('equal', adjustable='box')

def plot_closest(voters : list[Voter], candidates : list[Candidate],
                 cand_shifts : Optional[list[int]] = None, output_path : str = "./res_dis.png"):
    cand_shifts = [0 for _ in range(len(candidates))] if cand_shifts is None else cand_shifts
    fig, ax = plt.subplots()

    voter_points = [voter.coords for voter in voters]
    cand_points = [cand.coords for cand in candidates]

    closest_colours = [COLOURS[p + cand_shifts[p]] for p in closest_points(voter_points, cand_points, distance_euclid)]
    cand_colours = [COLOURS[i + cand_shifts[i]] for i in range(len(candidates))]
    scatter_agent_points(ax, voter_points, cand_points, closest_colours, cand_colours)
    fig.savefig(output_path)
    plt.close()

def plot_approved(voters : list[Voter], candidates : list[Candidate], output_path : str = "./res_dis.png"):
    fig, ax = plt.subplots()

    voter_points = [voter.coords for voter in voters]
    cand_points = [cand.coords for cand in candidates]

    closest_colours = [COLOURS[p] for p in closest_points(voter_points, cand_points, distance_euclid)]
    cand_colours = COLOURS[:len(candidates)]
    scatter_agent_points(ax, voter_points, cand_points, closest_colours, cand_colours)

    circles = [plt.Circle(voter.coords, radius_relative(voter.coords, cand_points, closest_w=voter.best_preference, furthest_w=voter.worst_tolerance), color=closest_colours[i], alpha=0.1) for i, voter in enumerate(voters)]
    for circle in circles:
        ax.add_patch(circle)

    fig.savefig(output_path)
    plt.close()

def plot_pie(votes_counts : list[int], params : dict[str, Any] = {}, cand_shifts : Optional[list[int]] = None, output_path : str = "./res_pie.png"):
    cand_shifts = [0 for _ in range(len(votes_counts))] if cand_shifts is None else cand_shifts
    cand_colours = [COLOURS[i + cand_shifts[i]] for i in range(len(votes_counts))]
    cand_names = [CAND_NAMES[i + cand_shifts[i]] for i in range(len(votes_counts))]
    fig, ax = plt.subplots()

    plt.title(params.get('title', "Unknown"))

    textstr = '\n'.join((
    r'VSE util = %.2f' % (params.get('vse_util', -1), ),
    r'VSE dist = %.2f' % (params.get('vse_dist', -1), ),
    r'VSE comp = %.2f' % (params.get('vse_comp', -1), )))

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    # place a text box in lower right (0.55, 0.30) or upper right (0.55, 0.98) in axes coords
    ax.text(1.03, 0.98, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    ax.pie(x=votes_counts, labels=cand_names, colors=cand_colours,
           autopct=lambda p : '{:.2f}%  ({:,.0f})'.format(p,p * sum(votes_counts)/100))
    plt.tight_layout()
    fig.savefig(output_path)
    plt.close()

def plot_bar(votes_counts : list[int], params : dict[str, Any] = {}, cand_shifts : Optional[list[int]] = None, output_path : str = "./res_bar.png"):
    cand_shifts = [0 for _ in range(len(votes_counts))] if cand_shifts is None else cand_shifts
    cand_colours = [COLOURS[i + cand_shifts[i]] for i in range(len(votes_counts))]
    cand_names = [CAND_NAMES[i + cand_shifts[i]] for i in range(len(votes_counts))]
    fig, ax = plt.subplots()

    plt.title(params.get('title', "Unknown"))

    textstr = '\n'.join((
    r'VSE util = %.2f' % (params.get('vse_util', -1), ),
    r'VSE dist = %.2f' % (params.get('vse_dist', -1), ),
    r'VSE comp = %.2f' % (params.get('vse_comp', -1), )))

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    # place a text box in lower right (0.55, 0.30) or upper right (0.55, 0.98) in axes coords
    ax.text(1.03, 0.98, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    ax.bar(x=cand_names, height=votes_counts, color=cand_colours)
    plt.tight_layout()
    fig.savefig(output_path)
    plt.close()

# TODO other types of plots
# TODO plot quality (VSE) dependent on parameters of system
