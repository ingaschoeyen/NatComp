from typing import Optional
import matplotlib.pyplot as plt
from voting import *
from voter import Strategy, Approach, Voter, Candidate

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

def plot_pie(votes_counts : list[int], cand_shifts : Optional[list[int]] = None, output_path : str = "./res_pie.png"):
    cand_shifts = [0 for _ in range(len(votes_counts))] if cand_shifts is None else cand_shifts
    cand_colours = [COLOURS[i + cand_shifts[i]] for i in range(len(votes_counts))]
    cand_names = [CAND_NAMES[i + cand_shifts[i]] for i in range(len(votes_counts))]
    fig, ax = plt.subplots()
    ax.pie(x=votes_counts, labels=cand_names, colors=cand_colours,
           autopct=lambda p : '{:.2f}%  ({:,.0f})'.format(p,p * sum(votes_counts)/100))
    fig.savefig(output_path)
    plt.close()

def plot_bar(votes_counts : list[int], cand_shifts : Optional[list[int]] = None, output_path : str = "./res_bar.png"):
    cand_shifts = [0 for _ in range(len(votes_counts))] if cand_shifts is None else cand_shifts
    cand_colours = [COLOURS[i + cand_shifts[i]] for i in range(len(votes_counts))]
    cand_names = [CAND_NAMES[i + cand_shifts[i]] for i in range(len(votes_counts))]
    fig, ax = plt.subplots()
    ax.bar(x=cand_names, height=votes_counts, color=cand_colours)
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
    results = [result['votes'] for result in simulation_results]
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
    plt.savefig(output_path)
    plt.close()
# TODO other types of plots


# TODO plot quality (VSE) dependent on parameters of system
