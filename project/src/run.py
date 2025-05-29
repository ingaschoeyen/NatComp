from plotting import *
from geometry import *
from voting import *
from voter import *

# TODO Create voters, candidates, run simulations, calculate and plot results, etc.
if __name__ == "__main__":
    voters = [Voter(point, Strategy.HONEST, 1, 1) for point in get_uniform(10)]
    candidates = [Candidate(point) for point in get_uniform(3)]

    threshold = 0.2
    polls = [0 for _ in range(len(candidates))] # TODO

    # First past the post
    votes_counts = fptp(voters, candidates, polls, threshold=0.0)
    results = percentage(votes_counts)
    plot_closest(voters, candidates, output_path="./fptp_vis.png")
    # plot_pie(votes_counts, output_path="./fptp_pie")
    plot_bar(votes_counts, output_path="./fptp_bar")
    print("fptp VSE:", vse_util(voters, candidates, results))
    votes_counts_trunc = trunc_votes(votes_counts, len(voters), threshold)
    results_trunc = percentage(votes_counts_trunc)
    plot_bar(votes_counts_trunc, output_path="./fptp_bar_trunc")
    print("fptp after trunc VSE", vse_util(voters, candidates, results_trunc))

    # Approval
    votes_counts = approval(voters, candidates, polls, threshold=0.0)
    results = percentage(votes_counts)
    plot_approved(voters, candidates, output_path="./app_vis.png")
    # plot_pie(votes_counts, output_path="./app_pie")
    plot_bar(votes_counts, output_path="./app_bar")
    print("app VSE:", vse_util(voters, candidates, results))
    votes_counts_trunc = trunc_votes(votes_counts, sum(votes_counts), threshold)
    results_trunc = percentage(votes_counts_trunc)
    plot_bar(votes_counts_trunc, output_path="./app_bar_trunc")
    print("app after trunc VSE", vse_util(voters, candidates, results_trunc))

    # Instant runoff
    votes_counts = instant_runoff(voters, candidates, polls, threshold)
    results = percentage(votes_counts)
    # plot_pie(votes_counts, output_path="./inst_pie")
    plot_bar(votes_counts, output_path="./inst_bar")
    print("Instanf runoff VSE:", vse_util(voters, candidates, results))

    # TODO plot how instant runoff eliminates candidates and counts votes

    final_results = [0 for _ in range(len(candidates))]
    candidates = [Candidate(cand.coords) for cand in candidates]
    polls = polls.copy()
    shifts = [0 for _ in range(len(candidates))]
    votes_counts = sum_votes(voters, candidates, polls, System.INSTANT_RUNOFF, dist_metric=distance_euclid)
    worst_cand = np.argmin(results)

    round = 0
    plot_closest(voters, candidates, cand_shifts=shifts, output_path="./inst_" + str(round) + "_vis.png")
    # plot_pie(votes_counts, output_path="./inst_" + str(round) + "_pie.png"
    plot_bar(votes_counts, cand_shifts=shifts, output_path="./inst_" + str(round) + "_bar.png")
    # print("Instanf runoff round", round, "VSE:", vse_util(voters, candidates, results))

    while votes_counts[worst_cand] / len(voters) < threshold:
        # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
        for i in range(worst_cand, len(candidates) - 1):
            shifts[i] = shifts[i + 1] + 1
        shifts.pop()
        candidates.pop(worst_cand)
        polls.pop(worst_cand)
        votes_counts = sum_votes(voters, candidates, polls, System.INSTANT_RUNOFF, dist_metric=distance_euclid)
        worst_cand = np.argmin(results)

        round += 1
        plot_closest(voters, candidates, cand_shifts=shifts, output_path="./inst_" + str(round) + "_vis.png")
        # plot_pie(votes_counts, output_path="./inst_" + str(round) + "_pie.png"
        plot_bar(votes_counts, cand_shifts=shifts, output_path="./inst_" + str(round) + "_bar.png")
        # print("Instanf runoff round", round, "VSE:", vse_util(voters, candidates, results))
