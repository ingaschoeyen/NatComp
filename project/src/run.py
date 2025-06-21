from plotting import *
from geometry import *
from voting import *
from agents import *
from election import *
from simulation import *


example_params = {
    # Election parameters
    "system" : System.INSTANT_RUNOFF,
    "threshold" : 0.1,
    "dist_metric" : distance_euclid,
    # Simulation parameters
    "n_rounds": 10,
    "n_polls": 5,
    # Population parameters
    "campaign_weight": 0.5,  # Weight of the campaign message in the voter's decision
    "poll_weight": 0.3,      # Weight of the polls in the voter's decision
    "social_weight": 0.2,    # Weight of the social influence in the voter's decision
    "dimension": 2,          # Dimension of the space in which voters and candidates are located
    "low": -1,               # Lower bound for the uniform distribution of voter positions
    "high": 1,               # Upper bound for the uniform distribution of voter positions
    "mu": 0,                 # Mean for the normal distribution of voter positions
    "sigma": 1,
    "cand_dist": Initialization.UNIFORM,  # Distribution type for candidate positions: "uniform", "normal", "cluster", or "custom"
    "n_candidates": 10,       # Number of candidates in the election
    "voter_dist": Initialization.UNIFORM, # Distribution type for voter positions: "uniform", "normal", "cluster", or "custom"
    "n_voters": 200,          # Number of voters in the population
    "use_local_neighborhood": False,  # Whether to use local neighborhood for updating voter opinions
    "neighborhood_radius": 0.2,  # Radius for the local neighborhood around
    "per_polls": 0.1,         # Percentage of the subsample size when polling
    # Voter parameters
    "best_preference": 0.5,  # Best ideological position for the voter
    "worst_tolerance": 0.1,  # Worst ideological position that the voter tolerates
    "campaign_weight": 0.4,  # Weight of the campaign message in the voter's decision
    "poll_weight": 0.2,  # Weight of the polls in the voter's decision
    "social_weight": 0.6,  # Weight of the social influence in the voter's decision
    # Candidate parameters
    "approach_weight": 0.005,  # Weight of the approach in the candidate's position update
    "cand_approach_dist": {
        Approach.RANDOM : 0.05,
        Approach.HONEST : 0.45,
        Approach.DEFENSIVE : 0.25,
        Approach.OFFENSIVE : 0.25
    },
    "voter_strat_dist": {
        Strategy.RANDOM : 0.05,
        Strategy.HONEST : 0.10,
        Strategy.POPULIST : 0.10,
        Strategy.REALIST : 0.50,
        Strategy.LOYAL : 0.25,
    },
}

if __name__ == "__main__":
    system = example_params['system']
    n_sims = 1
    total_output = []
    for i in range(n_sims):
        population = Population(params=example_params)
        voter_strategies, candidate_approaches = population.get_strategies()
        plot_population(voter_strategies, candidate_approaches, output_path=f"./population_distribution_sim_{i}_{system.name}.png")
        sim = Simulation(population=population, params=example_params)
        output = sim.run_election_cycles(save_results=False, plot_results=False, make_gif=True, delete_frames=False)
        plot_sim_dynamics(sim.output_sims.get('results'), output_path=f"./simulation_dynamics_sim{i}_{system.name}.png")
        total_output.append(output)

"""
def plot_results(votes_counts : list[float], title : str, plot_func, output_path : str):
    results = percentage(votes_counts)
    params = {}
    params['title'] = title
    params['vse_util'] = vse_util(voters, candidates, results)
    params['vse_dist'] = vse_vdist_comp(voters, candidates, results)
    params['vse_comp'] = vse_comp(voters, candidates, results)
    plot_func(results, params=params, output_path=output_path)


# TODO Create voters, candidates, run simulations, calculate and plot results, etc.
if __name__ == "__main__":
    voters = [Voter(point, Strategy.HONEST, best_preference=1, worst_tolerance=1) for point in get_uniform(1000)]
    candidates = [Candidate(point) for point in get_uniform(10)]

    threshold = 0.1
    polls = [0 for _ in range(len(candidates))] # TODO

    # Everyone gets the same amount of votes
    uniform_results = [1/len(candidates) for _ in candidates]
    plot_results(uniform_results, title="Uniform", plot_func=plot_bar, output_path="./uniform_bar.png")

    # One candidate gets all votes
    for cand in range(len(candidates)):
        results = [0 for _ in range(len(candidates))]
        results[cand] = 1
        plot_results(results, title="Only one candidate", plot_func=plot_bar, output_path="./onecand" + str(cand) + ".png")

    # Every candidate gets percentage according to their total utility
    utilities = total_utility(voters, candidates)
    plot_results(utilities, title="Compromise", plot_func=plot_bar, output_path="./compromise.png")

    # First past the post
    votes_counts = fptp(voters, candidates, polls, threshold=0.0)
    plot_closest(voters, candidates, output_path="./fptp_vis.png")
    plot_results(votes_counts, title="FPTP", plot_func=plot_bar, output_path="./fptp_bar")

    # First past the post truncated
    votes_counts_trunc = trunc_votes(votes_counts, len(voters), threshold)
    plot_results(votes_counts_trunc, title="FPTP truncated", plot_func=plot_bar, output_path="./fptp_bar_trunc")

    # Approval
    votes_counts = approval(voters, candidates, polls, threshold=0.0)
    plot_approved(voters, candidates, output_path="./app_vis.png")
    plot_results(votes_counts, title="Approval", plot_func=plot_bar, output_path="./app_bar")

    # Approval truncated
    votes_counts_trunc = trunc_votes(votes_counts, sum(votes_counts), threshold)
    plot_results(votes_counts_trunc, title="Approval truncated", plot_func=plot_bar, output_path="./app_bar_trunc")

    # Instant runoff
    votes_counts = instant_runoff(voters, candidates, polls, threshold)
    plot_results(votes_counts, title="Instant runoff", plot_func=plot_bar, output_path="./inst_bar")

    # TODO plot how instant runoff eliminates candidates and counts votes

    params = {}
    final_results = [0 for _ in range(len(candidates))]
    candidates = [Candidate(cand.coords) for cand in candidates]
    polls = polls.copy()
    shifts = [0 for _ in range(len(candidates))]
    votes_counts = sum_votes(voters, candidates, polls, System.INSTANT_RUNOFF, dist_metric=distance_euclid)
    worst_cand = np.argmin(votes_counts)

    round = 0
    plot_closest(voters, candidates, cand_shifts=shifts, output_path="./inst_" + str(round) + "_vis.png")
    # plot_pie(votes_counts, output_path="./inst_" + str(round) + "_pie.png"
    params['title'] = 'Instant runoff round ' + str(round)
    plot_bar(votes_counts, params=params, cand_shifts=shifts, output_path="./inst_" + str(round) + "_bar.png")

    while votes_counts[worst_cand] / len(voters) < threshold:
        # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
        for i in range(worst_cand, len(candidates) - 1):
            shifts[i] = shifts[i + 1] + 1
        shifts.pop()
        candidates.pop(worst_cand)
        polls.pop(worst_cand)
        votes_counts = sum_votes(voters, candidates, polls, System.INSTANT_RUNOFF, dist_metric=distance_euclid)
        worst_cand = np.argmin(votes_counts)

        round += 1
        plot_closest(voters, candidates, cand_shifts=shifts, output_path="./inst_" + str(round) + "_vis.png")
        # plot_pie(votes_counts, params=params, output_path="./inst_" + str(round) + "_pie.png"
        params['title'] = 'Instant runoff round ' + str(round)
        plot_bar(votes_counts, params=params, cand_shifts=shifts, output_path="./inst_" + str(round) + "_bar.png")
"""
