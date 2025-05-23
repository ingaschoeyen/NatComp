from plotting import *
from geometry import *
from voting import *

# TODO Create voters, candidates, run simulations, calculate and plot results, etc.
if __name__ == "__main__":
    voters, cands = Population(), Population()
    voters.init_normal(1000)
    cands.init_normal(10)

    threshold = 0.1

    # First past the post
    votes_counts = fptp(voters, cands)
    results = percentage(votes_counts)
    plot_closest(voters, cands, output_path="./fptp_vis.png")
    # plot_pie(votes_counts, output_path="./res_pie_fptp")
    plot_bar(votes_counts, output_path="./fptp_bar")
    print("fptp VSE:", vse_util(voters, cands, results))
    votes_counts_trunc = trunc_votes(votes_counts, voters.size(), threshold)
    results_trunc = percentage(votes_counts_trunc)
    plot_bar(votes_counts_trunc, output_path="./fptp_bar_trunc")
    print("fptp after trunc VSE", vse_util(voters, cands, results_trunc))

    radius = 0.5

    votes_counts = approval_best(voters, cands, radius)
    results = percentage(votes_counts)
    plot_approved(voters, cands, radius, radius_closest, "./app_closest_vis.png")
    # plot_pie(votes_counts, output_path="./res_pie_app_closest")
    plot_bar(votes_counts, output_path="./app_closest_bar")
    print("Approval best VSE:", vse_util(voters, cands, results))

    votes_counts = approval_worst(voters, cands, radius)
    results = percentage(votes_counts)
    plot_approved(voters, cands, radius, radius_furthest, "./app_furthest_vis.png")
    # plot_pie(votes_counts, output_path="./res_pie_app_furthest")
    plot_bar(votes_counts, output_path="./app_furthest_bar")
    print("Approval worst VSE:", vse_util(voters, cands, results))

    votes_counts = approval_between(voters, cands, radius)
    results = percentage(votes_counts)
    plot_approved(voters, cands, radius, radius_between, "./app_between_vis.png")
    # plot_pie(votes_counts, output_path="./res_pie_app_between")
    plot_bar(votes_counts, output_path="./app_between_bar")
    print("Approval between VSE:", vse_util(voters, cands, results))

    votes_counts = instant_runoff(voters, cands, threshold=threshold)
    results = percentage(votes_counts)
    # plot_pie(votes_counts, output_path="./res_pie_instant")
    plot_bar(votes_counts, output_path="./inst_bar")
    print("Instanf runoff VSE:", vse_util(voters, cands, results))

    # TODO plot how instant runoff eliminates candidates and counts votes

    candidates = cands.copy()
    round = 0
    shifts = [0 for _ in range(candidates.size())]
    votes_counts = fptp(voters, candidates, dist_metric=distance_euclid)
    results = percentage(votes_counts)
    worst_cand = np.argmin(votes_counts)
    plot_closest(voters, candidates, cand_shifts=shifts, output_path="./inst_" + str(round) + "_vis.png")
    # plot_pie(votes_counts, output_path="./vse_" + str(round) + "_pie.png"
    plot_bar(votes_counts, cand_shifts=shifts, output_path="./inst_" + str(round) + "_bar.png")
    print("Instanf runoff round", round, "VSE:", vse_util(voters, candidates, results))
    while results[worst_cand] <= threshold:
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
        print("Instanf runoff round", round, "VSE:", vse_util(voters, candidates, results))
