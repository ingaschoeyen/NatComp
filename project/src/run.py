from plotting import *
from geometry import *
from voting import *
from voter import *

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
