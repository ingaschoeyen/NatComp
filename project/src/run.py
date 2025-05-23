from plotting import *
from geometry import *
from voting import *

# TODO Create voters, candidates, run simulations, calculate and plot results, etc.
if __name__ == "__main__":
    voters, candidates = Population(), Population()
    voters.init_normal(20)
    candidates.init_normal(3)

    threshold = 0.1

    # First past the post
    votes_counts = fptp(voters, candidates)
    results = percentage(votes_counts)
    plot_closest(voters, candidates, output_path="./fptp_vis.png")
    # plot_pie(votes_counts, output_path="./fptp_pie")
    plot_bar(votes_counts, output_path="./fptp_bar")
    print("fptp VSE:", vse_util(voters, candidates, results))
    votes_counts_trunc = trunc_votes(votes_counts, voters.size(), threshold)
    results_trunc = percentage(votes_counts_trunc)
    plot_bar(votes_counts_trunc, output_path="./fptp_bar_trunc")
    print("fptp after trunc VSE", vse_util(voters, candidates, results_trunc))

    # Approval
    best_preference = 1
    worst_tolerance = 1

    votes_counts = approval_rel(voters, candidates, best_preference=best_preference, worst_tolerance=worst_tolerance)
    results = percentage(votes_counts)
    plot_approved_rel(voters, candidates, best_preference=best_preference, worst_tolerance=worst_tolerance, output_path="./app_rel_vis.png")
    # plot_pie(votes_counts, output_path="./app_rel_pie")
    plot_bar(votes_counts, output_path="./app_rel_bar")
    print("app rel VSE:", vse_util(voters, candidates, results))
    votes_counts_trunc = trunc_votes(votes_counts, sum(votes_counts), threshold)
    results_trunc = percentage(votes_counts_trunc)
    plot_bar(votes_counts_trunc, output_path="./app_rel_bar_trunc")
    print("app rel after trunc VSE", vse_util(voters, candidates, results_trunc))

    # Instant runoff
    votes_counts = instant_runoff(voters, candidates, threshold=threshold)
    results = percentage(votes_counts)
    # plot_pie(votes_counts, output_path="./inst_pie")
    plot_bar(votes_counts, output_path="./inst_bar")
    print("Instanf runoff VSE:", vse_util(voters, candidates, results))

    # TODO plot how instant runoff eliminates candidates and counts votes

    candidates = candidates.copy()
    round = 0
    shifts = [0 for _ in range(candidates.size())]
    votes_counts = fptp(voters, candidates, dist_metric=distance_euclid)
    results = percentage(votes_counts)
    worst_cand = np.argmin(votes_counts)
    plot_closest(voters, candidates, cand_shifts=shifts, output_path="./inst_" + str(round) + "_vis.png")
    # plot_pie(votes_counts, output_path="./vse_" + str(round) + "_pie.png"
    plot_bar(votes_counts, cand_shifts=shifts, output_path="./inst_" + str(round) + "_bar.png")
    # print("Instanf runoff round", round, "VSE:", vse_util(voters, candidates, results))
    while results[worst_cand] < threshold:
        # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
        for i in range(worst_cand, candidates.size() - 1):
            shifts[i] = shifts[i + 1] + 1
        shifts.pop()
        candidates.pop(worst_cand)
        votes_counts = fptp(voters, candidates, dist_metric=distance_euclid)
        results = percentage(votes_counts)
        worst_cand = np.argmin(votes_counts)
        round += 1

        plot_closest(voters, candidates, cand_shifts=shifts, output_path="./inst_" + str(round) + "_vis.png")
        # plot_pie(votes_counts, output_path="./inst_" + str(round) + "_pie.png"
        plot_bar(votes_counts, cand_shifts=shifts, output_path="./inst_" + str(round) + "_bar.png")
        # print("Instanf runoff round", round, "VSE:", vse_util(voters, candidates, results))
