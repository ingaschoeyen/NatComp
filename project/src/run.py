from plotting import *
from geometry import *
from voting import *

# TODO Create voters, candidates, run simulations, calculate and plot results, etc.
if __name__ == "__main__":
    voters, cands = Population(), Population()
    voters.init_uniform(10, 2)
    cands.init_uniform(3, 2)

    # First past the post
    results = fptp(voters, cands)
    plot_closest(voters, cands, "./res_dis.png")
    plot_pie(results, output_path="./res_pie_fptp")
    plot_bar(results, output_path="./res_bar_fptp")

    threshold = 0.5
    results = approval_best(voters, cands, threshold)
    plot_approved(voters, cands, threshold, radius_closest, "./res_app_closest.png")
    plot_pie(results, output_path="./res_pie_app_closest")
    plot_bar(results, output_path="./res_bar_app_closest")
    results = approval_worst(voters, cands, threshold)
    plot_approved(voters, cands, threshold, radius_furthest, "./res_app_furthest.png")
    plot_pie(results, output_path="./res_pie_app_furthest")
    plot_bar(results, output_path="./res_bar_app_furthest")
    results = approval_between(voters, cands, threshold)
    plot_approved(voters, cands, threshold, radius_between, "./res_app_between.png")
    plot_pie(results, output_path="./res_pie_app_between")
    plot_bar(results, output_path="./res_bar_app_between")

    # TODO plot how instant runoff eliminates candidates and counts votes

    # candidates = cands.copy()
    # round = 0
    # shifts = [0 for _ in range(candidates.size())]
    # results = fptp(voters, candidates, distance_euclid)
    # worst_cand = np.argmin(results)
    # plot_closest(voters, candidates, "./" + str(round) + "res_dis.png")
    # while results[worst_cand] / voters.size() <= 0.1:
    #     # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
    #     for i in range(worst_cand, candidates.size() - 1):
    #         shifts[i] = shifts[i + 1] + 1
    #     shifts.pop()
    #     candidates.pop(worst_cand)
    #     results = fptp(voters, candidates, distance_euclid)
    #     plot_closest(voters, candidates, "./" + str(round) + "res_dis.png")
    #     worst_cand = np.argmin(results)
    #     round += 1
