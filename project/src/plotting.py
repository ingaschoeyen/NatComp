from typing import Any, Optional
import matplotlib.pyplot as plt
import imageio as iio
from voting import *
from agents import Strategy, Approach, Voter, Candidate
import os
# Max 10
COLOURS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Max 26
CAND_NAMES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# Colours correspond to closest candidates
def scatter_agent_points(ax : plt.Axes, voters_points : list[Point], candidates_points : list[Point],
                         voter_colours : list[str], cand_colours : list[str]):
    voters_points = np.reshape(voters_points, (-1, 2))
    candidates_points = np.reshape(candidates_points, (-1, 2))
    ax.scatter(voters_points[:, 0], voters_points[:, 1],
               c=voter_colours,
               alpha=1)
    ax.scatter(candidates_points[:,0], candidates_points[:,1],
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
    # for circle in circles:
    #     ax.add_patch(circle)

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

def plot_population(strategies: list[Strategy], approaches: list[Approach], output_path: str = "./population_distribution.png"):
    # get voter strategies

    plt.subplots(1, 2, figsize=(10, 6))
    plt.subplot(1, 2, 1)
    plt.pie([strategies.count(strat.value) for strat in Strategy],
            labels=[strat.name for strat in Strategy],
            autopct='%1.1f%%',
            startangle=140,
            colors=COLOURS[:len(Strategy)])
    plt.title('Voter Strategy Distribution')
    plt.subplot(1, 2, 2)
    plt.pie([approaches.count(approach.value) for approach in Approach],
            labels=[approach.name for approach in Approach],
            autopct='%1.1f%%',
            startangle=140,
            colors=COLOURS[:len(Approach)])
    plt.tight_layout()
    plt.title('Candidate Approach Distribution')
    plt.savefig(output_path)

def plot_sim_dynamics(simulation_results: list, output_path: str = "./simulation_dynamics.png"):
    """
    Plot the dynamics of the simulation results over time.
    :param simulation_results: Dictionary containing simulation results with keys as round numbers and values as results.
    :param output_path: Path to save the plot.
    """

    rounds = len(simulation_results)
    results = [result['votes_per'] for result in simulation_results]
    cand_results = np.reshape(results[:], (rounds, len(results[0])))


    vse_util = [result['vse_util'] for result in simulation_results]
    vse_util = np.reshape(vse_util[:], (rounds, 1))

    vse_comp = [result['vse_comp'] for result in simulation_results]
    vse_comp = np.reshape(vse_comp[:], (rounds, 1))

    vse_vdist_comp = [result['vse_vdist_comp'] for result in simulation_results]
    vse_vdist_comp = np.reshape(vse_vdist_comp[:], (rounds, 1))

    plt.subplots(2, 1, figsize=(15, 10), height_ratios=[1, 4])
    plt.subplot(2, 1, 1)
    plt.plot(vse_util, label='VSE (util)', marker='o', linestyle='-')
    plt.plot(vse_comp, label='VSE (comp)', marker='o', linestyle='-')
    plt.plot(vse_vdist_comp, label='VSE (vdist comp)', marker='o', linestyle='-')
    plt.xlabel('Round')
    plt.ylabel('VSE')
    plt.title('Voter Satisfaction Efficiency')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.subplot(2,1,2)
    prev = 0
    for i in range(len(results[0])):
        plt.fill_between(range(rounds), prev, prev+cand_results[:, i], label=f'Candidate {i+1}', color=COLOURS[i % len(COLOURS)], alpha=0.5)
        prev += cand_results[:, i]

    plt.xlabel('Round')
    plt.ylabel('Votes')
    plt.title('Vote Composition')
    plt.legend(loc='center right', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    plt.savefig(output_path)
    plt.close()

def plot_dynamics(ax: plt.Axes, sim_res: list, pop_name: str):
    rounds = len(sim_res)
    results = [result['votes_per'] for result in sim_res]
    cand_results = np.reshape(results[:], (rounds, len(results[0])))

    prev = 0
    for i in range(len(results[0])):
        ax.fill_between(range(rounds), prev, prev+cand_results[:, i], label=f'Candidate {i+1}', color=COLOURS[i % len(COLOURS)], alpha=0.5)
        prev += cand_results[:, i]

    ax.set_xlabel('Round')
    ax.set_ylabel('Votes')
    ax.set_title(f'Vote Composition for {pop_name}')
    ax.legend(loc='center right', bbox_to_anchor=(1, 0.5))
    ax.grid()

def plot_stats(ax: plt.Axes, res: list, n_sims: int, n_rounds: int, pop_name: str):
    vse_comp, vse_util, vse_vdist_comp, norm_entropy = np.zeros((n_sims, n_rounds)), np.zeros((n_sims, n_rounds)), np.zeros((n_sims, n_rounds)), np.zeros((n_sims, n_rounds))
    for j, results in enumerate(res):
        vse_comp[j, :] = np.reshape([r.get('vse_comp')  for r in results], (1, n_rounds))
        vse_util[j, :] = np.reshape([r.get('vse_util') for r in results], (1, n_rounds))
        vse_vdist_comp[j, :] = np.reshape([r.get('vse_vdist_comp') for r in results], (1, n_rounds))
        norm_entropy = np.reshape([r.get('norm_entropy') for r in results], (1, n_rounds))
    # average over simulations
    vse_comp_mean = np.mean(vse_comp, axis=0)
    vse_util_mean = np.mean(vse_util, axis=0)
    vse_vdist_comp_mean = np.mean(vse_vdist_comp, axis=0)
    norm_entropy_mean = np.mean(norm_entropy, axis=0)
    # get std
    vse_comp_std = np.std(vse_comp, axis=0)
    vse_util_std = np.std(vse_util, axis=0)
    vse_vdist_comp_std = np.std(vse_vdist_comp, axis=0)
    norm_entropy_std = np.std(norm_entropy, axis=0)
    # plot results

    ax.plot(vse_comp_mean, label='VSE Comp', color='blue')
    ax.fill_between(range(n_rounds), vse_comp_mean - vse_comp_std, vse_comp_mean + vse_comp_std, color='blue', alpha=0.2)
    ax.plot(vse_util_mean, label='VSE Util', color='orange')
    ax.fill_between(range(n_rounds), vse_util_mean - vse_util_std, vse_util_mean + vse_util_std, color='orange', alpha=0.2)
    ax.plot(vse_vdist_comp_mean, label='VSE VDist Comp', color='green')
    ax.fill_between(range(n_rounds), vse_vdist_comp_mean - vse_vdist_comp_std, vse_vdist_comp_mean + vse_vdist_comp_std, color='green', alpha=0.2)
    ax.plot(norm_entropy_mean, label='Norm Entropy', color='red')
    ax.fill_between(range(n_rounds), norm_entropy_mean - norm_entropy_std, norm_entropy_mean + norm_entropy_std, color='red', alpha=0.2)
    ax.set_title(f'Simulation Results for {pop_name}')
    ax.set_xlabel('Round')
    ax.set_ylabel('Value')
    ax.legend()
    ax.grid()

def get_gif_scatter(voters: list[Voter], candidates: list[Candidate], polls: list[float], results: list[float], system: System, cur_round, vse_util, output_path: str = "./election_gif_frame.png"):

    max_radius = 1000 # radius of the max size of candidates to multiply by results
    min_radius = 100  # radius of the min size of candidates (in case they do not get many votes)
    fig, ax = plt.subplots(1, 3, figsize=(10, 5))
    plt.subplot(1, 3, 1)

    ax[0].set_xlim(-1.1, 1.1)
    ax[0].set_ylim(-1.1, 1.1)
    voters_points = [voter.coords for voter in voters]
    cands_points = [cand.coords for cand in candidates]
    voters_points = np.reshape(voters_points, (-1, 2))
    cands_points = np.reshape(cands_points, (-1, 2))
    voter_colours = [COLOURS[np.argmax(voter.get_votes(candidates, polls=polls, system=system, dist_metric=distance_euclid))] for voter in voters]
    cand_colours = [COLOURS[i] for i in range(len(candidates))]

    voter_strat_symbol = {
        Strategy.HONEST : "$H$",
        Strategy.LOYAL : "$L$",
        Strategy.RANDOM : "$?$",
        Strategy.POPULIST : "$P$",
        Strategy.REALIST : "$R$"}

    for i, voter in enumerate(voters):
        ax[0].scatter(voters_points[i, 0], voters_points[i, 1], c=voter_colours[i], alpha=1, label=[voter.strat.name], marker=voter_strat_symbol[voter.strat])

    ax[0].scatter(cands_points[:,0], cands_points[:,1],
               c=cand_colours,
               s=[max(max_radius * result, min_radius) for result in results],
               alpha=0.5, label=[cand.approach.name for cand in candidates])
    ax[0].set_aspect('equal', adjustable='box')
    ax[0].text(-0.3, 1.15, f"VSE (util): {round(vse_util, 2)}", transform=ax[0].transAxes, fontsize=12, verticalalignment='top')

    plt.subplot(1, 3, 2)
    ax[1].bar(x=CAND_NAMES[:len(candidates)], height=polls, color=cand_colours)
    ax[1].set_xlabel('Candidates')
    ax[1].set_ylabel('Polls Vote Share')

    plt.subplot(1, 3, 3)
    ax[2].bar(x=CAND_NAMES[:len(candidates)], height=results, color=cand_colours)
    ax[2].set_xlabel('Candidates')
    ax[2].set_ylabel('Election Vote Share')
    fig.suptitle(f"Round {cur_round} - {system.name} System")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)

    return fig, output_path  # Return the path to the saved image for GIF creation

# TODO plot quality (VSE) dependent on parameters of system
def make_gif_scatter(frames, output_path: str = "./election.gif", delete_frames: bool = True):
    gif_ims = []
    for frame in frames:
        gif_ims.append(iio.imread(frame))
    iio.mimsave(output_path, gif_ims)
    if delete_frames:
        for gif_im in frames:
            # delete the frame file
            os.remove(gif_im)


